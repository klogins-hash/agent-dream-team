"""Agent-First DevOps - Autonomous deployment, monitoring, and self-healing."""

import os
import subprocess
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml
import kubernetes

from database import get_postgres
from messaging import get_message_broker
from agent_workflow import get_workflow_engine


@dataclass
class DeploymentConfig:
    """Deployment configuration for agents."""
    name: str
    image: str
    replicas: int = 1
    resources: Dict[str, str] = None
    environment: Dict[str, str] = None
    health_check: Dict[str, Any] = None
    auto_scale: bool = True
    rollback_on_failure: bool = True


class AgentDevOps:
    """Agent-first DevOps automation system."""
    
    def __init__(self):
        """Initialize DevOps system."""
        self.db = get_postgres()
        self.message_broker = get_message_broker()
        self.workflow_engine = get_workflow_engine()
        self.deployment_history: List[Dict[str, Any]] = []
        self.monitoring_alerts: List[Dict[str, Any]] = []
        
        # Initialize Kubernetes client if available
        self.k8s_enabled = self._init_kubernetes()
    
    def _init_kubernetes(self) -> bool:
        """Initialize Kubernetes client."""
        try:
            kubernetes.config.load_incluster_config()  # For in-cluster
            self.k8s_client = kubernetes.client.CoreV1Api()
            self.k8s_apps = kubernetes.client.AppsV1Api()
            return True
        except:
            try:
                kubernetes.config.load_kube_config()  # For local development
                self.k8s_client = kubernetes.client.CoreV1Api()
                self.k8s_apps = kubernetes.client.AppsV1Api()
                return True
            except:
                print("Kubernetes not available, using Docker-based deployment")
                return False
    
    async def autonomous_deployment(self, config: DeploymentConfig, triggered_by: str = "system") -> str:
        """Autonomous deployment triggered by agent decision."""
        deployment_id = f"deploy-{config.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Log deployment decision
        deployment_record = {
            "id": deployment_id,
            "config": config.__dict__,
            "triggered_by": triggered_by,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.deployment_history.append(deployment_record)
        
        try:
            # Pre-deployment checks
            await self._pre_deployment_checks(config)
            
            # Execute deployment
            if self.k8s_enabled:
                result = await self._deploy_to_kubernetes(config, deployment_id)
            else:
                result = await self._deploy_to_docker(config, deployment_id)
            
            # Post-deployment validation
            await self._post_deployment_validation(config, deployment_id)
            
            deployment_record["status"] = "success"
            deployment_record["result"] = result
            
            # Notify agents
            await self._notify_deployment_success(deployment_id, config, triggered_by)
            
        except Exception as e:
            deployment_record["status"] = "failed"
            deployment_record["error"] = str(e)
            
            # Auto-rollback if enabled
            if config.rollback_on_failure:
                await self._auto_rollback(deployment_id, config)
            
            # Notify agents of failure
            await self._notify_deployment_failure(deployment_id, config, str(e), triggered_by)
        
        finally:
            await self._persist_deployment_record(deployment_record)
        
        return deployment_id
    
    async def _pre_deployment_checks(self, config: DeploymentConfig):
        """Run pre-deployment checks."""
        # Check image availability
        if not await self._check_image_availability(config.image):
            raise Exception(f"Image {config.image} not available")
        
        # Check resource availability
        if not await self._check_resource_availability(config):
            raise Exception("Insufficient resources")
        
        # Check configuration validity
        if not await self._validate_config(config):
            raise Exception("Invalid deployment configuration")
    
    async def _deploy_to_kubernetes(self, config: DeploymentConfig, deployment_id: str) -> Dict[str, Any]:
        """Deploy to Kubernetes cluster."""
        # Create deployment manifest
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": deployment_id,
                "labels": {
                    "app": config.name,
                    "deployment": deployment_id,
                    "managed-by": "agent-devops"
                }
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.name,
                            "deployment": deployment_id
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": config.name,
                            "image": config.image,
                            "env": [
                                {"name": k, "value": v}
                                for k, v in (config.environment or {}).items()
                            ],
                            "resources": {
                                "requests": config.resources or {"memory": "256Mi", "cpu": "250m"},
                                "limits": config.resources or {"memory": "512Mi", "cpu": "500m"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Apply deployment
        self.k8s_apps.create_namespaced_deployment(
            namespace="default",
            body=manifest
        )
        
        # Wait for deployment to be ready
        await self._wait_for_kubernetes_deployment(deployment_id)
        
        return {"platform": "kubernetes", "deployment_id": deployment_id}
    
    async def _deploy_to_docker(self, config: DeploymentConfig, deployment_id: str) -> Dict[str, Any]:
        """Deploy using Docker Compose."""
        # Generate docker-compose override
        compose_override = {
            "version": "3.8",
            "services": {
                config.name: {
                    "image": config.image,
                    "environment": config.environment or {},
                    "deploy": {
                        "replicas": config.replicas,
                        "resources": {
                            "limits": config.resources or {"memory": "512M", "cpus": "0.5"}
                        }
                    },
                    "healthcheck": config.health_check or {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                }
            }
        }
        
        # Write override file
        override_file = f"docker-compose.{deployment_id}.override.yml"
        with open(override_file, "w") as f:
            yaml.dump(compose_override, f)
        
        # Deploy
        cmd = f"docker-compose -f docker-compose.yml -f {override_file} up -d"
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Docker deployment failed: {result.stderr}")
        
        # Cleanup override file
        os.remove(override_file)
        
        return {"platform": "docker", "deployment_id": deployment_id}
    
    async def _post_deployment_validation(self, config: DeploymentConfig, deployment_id: str):
        """Validate deployment after rollout."""
        # Health checks
        if not await self._verify_health_checks(config, deployment_id):
            raise Exception("Health checks failed")
        
        # Performance validation
        if not await self._verify_performance(config, deployment_id):
            raise Exception("Performance validation failed")
        
        # Integration tests
        if not await self._run_integration_tests(config, deployment_id):
            raise Exception("Integration tests failed")
    
    async def continuous_monitoring(self):
        """Continuous monitoring and self-healing."""
        while True:
            try:
                # Check deployment health
                await self._check_all_deployments()
                
                # Check resource utilization
                await self._check_resource_utilization()
                
                # Check for alerts
                await self._process_monitoring_alerts()
                
                # Auto-scaling decisions
                await self._make_auto_scaling_decisions()
                
                # Self-healing actions
                await self._execute_self_healing()
                
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def _check_all_deployments(self):
        """Check health of all deployments."""
        if self.k8s_enabled:
            # Check Kubernetes deployments
            deployments = self.k8s_apps.list_namespaced_deployment(namespace="default")
            
            for deployment in deployments.items:
                if "managed-by" not in deployment.metadata.labels:
                    continue
                
                deployment_id = deployment.metadata.name
                app_name = deployment.metadata.labels.get("app")
                
                # Check replica status
                if deployment.status.ready_replicas != deployment.spec.replicas:
                    await self._handle_deployment_issue(deployment_id, "replica_mismatch")
                
                # Check pod health
                pods = self.k8s_client.list_namespaced_pod(
                    namespace="default",
                    label_selector=f"deployment={deployment_id}"
                )
                
                for pod in pods.items:
                    if pod.status.phase != "Running":
                        await self._handle_pod_issue(deployment_id, pod.metadata.name, pod.status.phase)
    
    async def _make_auto_scaling_decisions(self):
        """Make autonomous scaling decisions based on metrics."""
        # Get performance metrics
        metrics = self.workflow_engine.get_performance_metrics()
        
        # Analyze metrics and make scaling decisions
        for agent_name, agent_metrics in metrics.items():
            # Scale up if success rate is high and duration is long (overloaded)
            if (agent_metrics["success_rate"] > 0.9 and 
                agent_metrics["avg_duration"] > 10):  # 10 seconds threshold
                
                await self._scale_up_agent(agent_name)
            
            # Scale down if underutilized
            elif (agent_metrics["success_rate"] > 0.95 and 
                  agent_metrics["avg_duration"] < 2):  # 2 seconds threshold
                
                await self._scale_down_agent(agent_name)
    
    async def _scale_up_agent(self, agent_name: str):
        """Scale up agent deployment."""
        if not self.k8s_enabled:
            return
        
        # Find deployment for agent
        deployments = self.k8s_apps.list_namespaced_deployment(namespace="default")
        
        for deployment in deployments.items:
            if deployment.metadata.labels.get("app") == agent_name:
                current_replicas = deployment.spec.replicas
                new_replicas = min(current_replicas + 1, 5)  # Max 5 replicas
                
                # Scale deployment
                patch = {"spec": {"replicas": new_replicas}}
                self.k8s_apps.patch_namespaced_deployment(
                    name=deployment.metadata.name,
                    namespace="default",
                    body=patch
                )
                
                # Log scaling decision
                await self._log_scaling_decision(agent_name, "up", current_replicas, new_replicas)
                break
    
    async def _scale_down_agent(self, agent_name: str):
        """Scale down agent deployment."""
        if not self.k8s_enabled:
            return
        
        # Find deployment for agent
        deployments = self.k8s_apps.list_namespaced_deployment(namespace="default")
        
        for deployment in deployments.items:
            if deployment.metadata.labels.get("app") == agent_name:
                current_replicas = deployment.spec.replicas
                new_replicas = max(current_replicas - 1, 1)  # Min 1 replica
                
                if new_replicas != current_replicas:
                    # Scale deployment
                    patch = {"spec": {"replicas": new_replicas}}
                    self.k8s_apps.patch_namespaced_deployment(
                        name=deployment.metadata.name,
                        namespace="default",
                        body=patch
                    )
                    
                    # Log scaling decision
                    await self._log_scaling_decision(agent_name, "down", current_replicas, new_replicas)
                break
    
    async def agent_triggered_rollback(self, deployment_id: str, reason: str, triggered_by: str):
        """Rollback triggered by agent decision."""
        deployment_record = next(
            (d for d in self.deployment_history if d["id"] == deployment_id),
            None
        )
        
        if not deployment_record:
            raise Exception(f"Deployment {deployment_id} not found")
        
        # Execute rollback
        if self.k8s_enabled:
            await self._rollback_kubernetes_deployment(deployment_id)
        else:
            await self._rollback_docker_deployment(deployment_id)
        
        # Log rollback
        rollback_record = {
            "deployment_id": deployment_id,
            "reason": reason,
            "triggered_by": triggered_by,
            "timestamp": datetime.now().isoformat()
        }
        
        # Notify agents
        await self._notify_rollback(deployment_id, reason, triggered_by)
    
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        deployment_record = next(
            (d for d in self.deployment_history if d["id"] == deployment_id),
            None
        )
        
        if not deployment_record:
            return None
        
        # Get live status if Kubernetes
        if self.k8s_enabled:
            try:
                deployment = self.k8s_apps.read_namespaced_deployment(
                    name=deployment_id,
                    namespace="default"
                )
                
                deployment_record["live_status"] = {
                    "replicas": deployment.spec.replicas,
                    "ready_replicas": deployment.status.ready_replicas,
                    "available_replicas": deployment.status.available_replicas,
                    "conditions": [
                        {
                            "type": cond.type,
                            "status": cond.status,
                            "reason": cond.reason
                        }
                        for cond in deployment.status.conditions or []
                    ]
                }
            except:
                pass
        
        return deployment_record
    
    async def _notify_deployment_success(self, deployment_id: str, config: DeploymentConfig, triggered_by: str):
        """Notify agents of successful deployment."""
        message = {
            "event": "deployment_success",
            "deployment_id": deployment_id,
            "service": config.name,
            "triggered_by": triggered_by,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.message_broker.broadcast_message("agent.notifications", message)
    
    async def _notify_deployment_failure(self, deployment_id: str, config: DeploymentConfig, error: str, triggered_by: str):
        """Notify agents of deployment failure."""
        message = {
            "event": "deployment_failure",
            "deployment_id": deployment_id,
            "service": config.name,
            "error": error,
            "triggered_by": triggered_by,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.message_broker.broadcast_message("agent.notifications", message)
    
    async def _persist_deployment_record(self, record: Dict[str, Any]):
        """Persist deployment record to database."""
        await self.db.cache.set(
            f"deployment:{record['id']}",
            json.dumps(record),
            expire=86400 * 7  # 7 days
        )


# Singleton instance
_agent_devops = None

def get_agent_devops() -> AgentDevOps:
    """Get agent DevOps instance."""
    global _agent_devops
    if _agent_devops is None:
        _agent_devops = AgentDevOps()
        # Start monitoring loop
        asyncio.create_task(_agent_devops.continuous_monitoring())
    return _agent_devops
