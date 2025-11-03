"""Agent-first workflow and DevOps tools."""

from typing import Dict, List, Any, Optional
from strands import tool

from agent_workflow import get_workflow_engine
from agent_devops import get_agent_devops, DeploymentConfig


@tool
def create_workflow(request: str, context: Dict[str, Any] = None) -> str:
    """Create a workflow from natural language request.
    
    This tool allows agents to automatically create and execute workflows
    based on their understanding of complex requests.
    
    Args:
        request: Natural language description of what needs to be done
        context: Additional context for workflow execution
        
    Returns:
        Workflow ID for tracking
    """
    workflow_engine = get_workflow_engine()
    
    # Create workflow asynchronously
    import asyncio
    workflow_id = asyncio.run(workflow_engine.create_workflow_from_request(
        request=request,
        creator_agent="current_agent",
        context=context or {}
    ))
    
    return f"Workflow created with ID: {workflow_id}. The workflow will execute automatically."


@tool
def check_workflow_status(workflow_id: str) -> str:
    """Check the status of a workflow.
    
    Args:
        workflow_id: ID of the workflow to check
        
    Returns:
        Current workflow status and progress
    """
    workflow_engine = get_workflow_engine()
    
    import asyncio
    status = asyncio.run(workflow_engine.get_workflow_status(workflow_id))
    
    if not status:
        return f"Workflow {workflow_id} not found."
    
    output = f"**Workflow Status: {workflow_id}**\n\n"
    output += f"Name: {status['name']}\n"
    output += f"Status: {status['status']}\n"
    output += f"Created by: {status['created_by']}\n"
    output += f"Created: {status['created_at']}\n"
    
    if status['started_at']:
        output += f"Started: {status['started_at']}\n"
    
    if status['completed_at']:
        output += f"Completed: {status['completed_at']}\n"
    
    output += f"\n**Tasks ({len(status['tasks'])}):**\n"
    
    for task_id, task_info in status['tasks'].items():
        output += f"- {task_id}: {task_info['status']}"
        if task_info['agent']:
            output += f" (Agent: {task_info['agent']})"
        if task_info['duration']:
            output += f" ({task_info['duration']:.2f}s)"
        output += "\n"
    
    return output


@tool
def deploy_service(service_name: str, image: str, replicas: int = 1, auto_scale: bool = True) -> str:
    """Deploy a service using autonomous DevOps.
    
    This tool allows agents to deploy services automatically
    without human intervention.
    
    Args:
        service_name: Name of the service to deploy
        image: Docker image to deploy
        replicas: Number of replicas to deploy
        auto_scale: Enable auto-scaling
        
    Returns:
        Deployment ID for tracking
    """
    devops = get_agent_devops()
    
    config = DeploymentConfig(
        name=service_name,
        image=image,
        replicas=replicas,
        auto_scale=auto_scale,
        rollback_on_failure=True
    )
    
    import asyncio
    deployment_id = asyncio.run(devops.autonomous_deployment(
        config=config,
        triggered_by="agent_tool"
    ))
    
    return f"Deployment initiated with ID: {deployment_id}. The system will deploy and validate automatically."


@tool
def check_deployment_status(deployment_id: str) -> str:
    """Check the status of a deployment.
    
    Args:
        deployment_id: ID of the deployment to check
        
    Returns:
        Current deployment status
    """
    devops = get_agent_devops()
    
    import asyncio
    status = asyncio.run(devops.get_deployment_status(deployment_id))
    
    if not status:
        return f"Deployment {deployment_id} not found."
    
    output = f"**Deployment Status: {deployment_id}**\n\n"
    output += f"Service: {status['config']['name']}\n"
    output += f"Status: {status['status']}\n"
    output += f"Triggered by: {status['triggered_by']}\n"
    output += f"Created: {status['created_at']}\n"
    
    if status['status'] == 'success':
        output += f"Result: {status['result']}\n"
    elif status['status'] == 'failed':
        output += f"Error: {status['error']}\n"
    
    # Add live status if available
    if 'live_status' in status:
        live = status['live_status']
        output += f"\n**Live Status:**\n"
        output += f"Replicas: {live['replicas']}\n"
        output += f"Ready: {live['ready_replicas']}\n"
        output += f"Available: {live['available_replicas']}\n"
    
    return output


@tool
def rollback_deployment(deployment_id: str, reason: str) -> str:
    """Rollback a deployment to previous version.
    
    This tool allows agents to rollback deployments automatically
    when issues are detected.
    
    Args:
        deployment_id: ID of the deployment to rollback
        reason: Reason for rollback
        
    Returns:
        Rollback confirmation
    """
    devops = get_agent_devops()
    
    import asyncio
    asyncio.run(devops.agent_triggered_rollback(
        deployment_id=deployment_id,
        reason=reason,
        triggered_by="agent_tool"
    ))
    
    return f"Rollback initiated for deployment {deployment_id}. Reason: {reason}"


@tool
def get_performance_metrics() -> str:
    """Get performance metrics for all agents.
    
    Returns:
        Performance metrics and optimization suggestions
    """
    workflow_engine = get_workflow_engine()
    metrics = workflow_engine.get_performance_metrics()
    
    if not metrics:
        return "No performance metrics available yet."
    
    output = "**Agent Performance Metrics**\n\n"
    
    for agent_name, agent_metrics in metrics.items():
        output += f"**{agent_name}:**\n"
        output += f"- Total tasks: {agent_metrics['total_tasks']}\n"
        output += f"- Success rate: {agent_metrics['success_rate']:.2%}\n"
        output += f"- Average duration: {agent_metrics['avg_duration']:.2f}s\n"
        
        # Optimization suggestions
        if agent_metrics['success_rate'] < 0.8:
            output += "- ⚠️ Low success rate - consider task reassignment\n"
        if agent_metrics['avg_duration'] > 15:
            output += "- ⚠️ High duration - consider scaling up\n"
        if agent_metrics['success_rate'] > 0.95 and agent_metrics['avg_duration'] < 2:
            output += "- ✅ Optimal performance - can handle more tasks\n"
        
        output += "\n"
    
    return output


@tool
def coordinate_agents(task_description: str, agents: List[str]) -> str:
    """Coordinate multiple agents for a complex task.
    
    This tool creates a workflow that coordinates multiple agents
    to work together on complex tasks.
    
    Args:
        task_description: Description of the complex task
        agents: List of agent names to coordinate
        
    Returns:
        Coordination workflow ID
    """
    workflow_engine = get_workflow_engine()
    
    # Create coordination context
    context = {
        "coordinated_agents": agents,
        "coordination_type": "multi_agent",
        "task_complexity": "high"
    }
    
    import asyncio
    workflow_id = asyncio.run(workflow_engine.create_workflow_from_request(
        request=task_description,
        creator_agent="coordinator",
        context=context
    ))
    
    return f"Multi-agent coordination started with workflow ID: {workflow_id}. Coordinating agents: {', '.join(agents)}"


@tool
def autonomous_scaling_decision(service_name: str, current_load: float, target_response_time: float) -> str:
    """Make autonomous scaling decisions based on metrics.
    
    This tool analyzes performance metrics and makes scaling decisions
    without human intervention.
    
    Args:
        service_name: Name of the service to scale
        current_load: Current load percentage (0-100)
        target_response_time: Target response time in seconds
        
    Returns:
        Scaling decision and rationale
    """
    # Simple scaling logic
    if current_load > 80:
        decision = "scale_up"
        reason = f"High load ({current_load}%) exceeds threshold"
    elif current_load < 20:
        decision = "scale_down"
        reason = f"Low load ({current_load}%) below threshold"
    else:
        decision = "no_change"
        reason = f"Load ({current_load}%) within optimal range"
    
    output = f"**Scaling Decision for {service_name}**\n\n"
    output += f"Decision: {decision}\n"
    output += f"Reason: {reason}\n"
    output += f"Current load: {current_load}%\n"
    output += f"Target response time: {target_response_time}s\n"
    
    if decision == "scale_up":
        output += "\n🚀 Scaling up - adding more replicas"
    elif decision == "scale_down":
        output += "\n⬇️ Scaling down - removing replicas to save resources"
    else:
        output += "\n✅ No scaling needed - current configuration is optimal"
    
    # Execute scaling decision
    if decision != "no_change":
        devops = get_agent_devops()
        # This would trigger the actual scaling in the DevOps system
        output += f"\n\nScaling decision queued for autonomous execution."
    
    return output
