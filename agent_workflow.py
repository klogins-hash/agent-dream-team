"""Agent-First Workflow Engine - Optimized for autonomous agent collaboration."""

import asyncio
import uuid
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime

from messaging import get_message_broker
from database import get_postgres
from neo4j_graph import get_knowledge_graph


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"  # Waiting for agent response
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskType(Enum):
    """Types of workflow tasks."""
    AGENT_TASK = "agent_task"
    DECISION = "decision"
    PARALLEL = "parallel"
    SEQUENCE = "sequence"
    CONDITION = "condition"
    HUMAN_INPUT = "human_input"  # Only when absolutely necessary


@dataclass
class WorkflowTask:
    """Individual task in a workflow."""
    id: str
    type: TaskType
    agent: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300  # 5 minutes default
    result: Any = None
    error: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Workflow:
    """Agent-first workflow definition."""
    id: str
    name: str
    description: str
    tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_by: str = "system"  # Agent that created it
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_history: List[Dict[str, Any]] = field(default_factory=list)


class AgentWorkflowEngine:
    """Agent-first workflow execution engine."""
    
    def __init__(self):
        """Initialize workflow engine."""
        self.message_broker = get_message_broker()
        self.db = get_postgres()
        self.kg = get_knowledge_graph()
        self.active_workflows: Dict[str, Workflow] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default task handlers."""
        self.task_handlers.update({
            TaskType.AGENT_TASK: self._handle_agent_task,
            TaskType.DECISION: self._handle_decision,
            TaskType.PARALLEL: self._handle_parallel,
            TaskType.SEQUENCE: self._handle_sequence,
            TaskType.CONDITION: self._handle_condition,
        })
    
    async def create_workflow_from_request(self, request: str, creator_agent: str, context: Dict[str, Any] = None) -> str:
        """Create workflow from natural language request.
        
        This is the agent-first approach - workflows are created dynamically
        based on agent understanding of the request.
        """
        workflow_id = str(uuid.uuid4())
        
        # Analyze request and decompose into tasks
        tasks = await self._analyze_and_decompose(request, context or {})
        
        workflow = Workflow(
            id=workflow_id,
            name=f"Auto-generated: {request[:50]}...",
            description=request,
            tasks=tasks,
            context=context or {},
            created_by=creator_agent
        )
        
        # Store workflow
        self.active_workflows[workflow_id] = workflow
        await self._persist_workflow(workflow)
        
        # Start execution immediately
        asyncio.create_task(self.execute_workflow(workflow_id))
        
        return workflow_id
    
    async def _analyze_and_decompose(self, request: str, context: Dict[str, Any]) -> Dict[str, WorkflowTask]:
        """Analyze request and decompose into tasks using agent intelligence."""
        tasks = {}
        
        # Simple decomposition logic - in production, this would use LLM
        if "research" in request.lower() and "write" in request.lower():
            # Research and write workflow
            tasks["research"] = WorkflowTask(
                id="research",
                type=TaskType.AGENT_TASK,
                agent="researcher",
                input_data={"request": request, "context": context}
            )
            
            tasks["write"] = WorkflowTask(
                id="write",
                type=TaskType.AGENT_TASK,
                agent="writer",
                input_data={"request": request, "context": context},
                dependencies=["research"]
            )
            
            tasks["review"] = WorkflowTask(
                id="review",
                type=TaskType.AGENT_TASK,
                agent="reviewer",
                input_data={"request": request, "context": context},
                dependencies=["write"]
            )
        
        elif "analyze" in request.lower():
            # Analysis workflow
            tasks["analyze"] = WorkflowTask(
                id="analyze",
                type=TaskType.AGENT_TASK,
                agent="coordinator",
                input_data={"request": request, "context": context}
            )
            
            tasks["validate"] = WorkflowTask(
                id="validate",
                type=TaskType.DECISION,
                conditions={"confidence_threshold": 0.8},
                dependencies=["analyze"]
            )
        
        else:
            # Simple single-agent task
            tasks["main"] = WorkflowTask(
                id="main",
                type=TaskType.AGENT_TASK,
                agent="coordinator",
                input_data={"request": request, "context": context}
            )
        
        return tasks
    
    async def execute_workflow(self, workflow_id: str):
        """Execute a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        try:
            # Execute tasks based on dependencies
            while not self._is_workflow_complete(workflow):
                # Find ready tasks
                ready_tasks = self._get_ready_tasks(workflow)
                
                if not ready_tasks:
                    # Check for stuck workflows
                    if self._is_workflow_stuck(workflow):
                        workflow.status = WorkflowStatus.FAILED
                        break
                    
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks in parallel
                await asyncio.gather(*[
                    self._execute_task(workflow, task_id)
                    for task_id in ready_tasks
                ])
            
            if workflow.status != WorkflowStatus.FAILED:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now()
            
            # Update performance metrics
            self._update_performance_metrics(workflow)
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "event": "workflow_failed",
                "error": str(e)
            })
        
        finally:
            await self._persist_workflow(workflow)
    
    async def _execute_task(self, workflow: Workflow, task_id: str):
        """Execute a single task."""
        task = workflow.tasks[task_id]
        
        if task.status != WorkflowStatus.PENDING:
            return
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            handler = self.task_handlers.get(task.type)
            if handler:
                result = await handler(workflow, task)
                task.result = result
                task.status = WorkflowStatus.COMPLETED
                task.completed_at = datetime.now()
            else:
                raise Exception(f"No handler for task type: {task.type}")
        
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count <= task.max_retries:
                task.status = WorkflowStatus.RETRYING
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                task.status = WorkflowStatus.PENDING
            else:
                task.status = WorkflowStatus.FAILED
        
        workflow.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "event": "task_executed",
            "task_id": task_id,
            "status": task.status.value,
            "agent": task.agent,
            "duration": (task.completed_at - task.started_at).total_seconds() if task.completed_at else None
        })
    
    async def _handle_agent_task(self, workflow: Workflow, task: WorkflowTask) -> Any:
        """Handle agent task execution."""
        # Send task to agent via message broker
        task_queue = f"agent.{task.agent}.tasks"
        
        message = {
            "workflow_id": workflow.id,
            "task_id": task.id,
            "input_data": task.input_data,
            "context": workflow.context
        }
        
        # Send task and wait for response
        await self.message_broker.send_message(task_queue, message)
        
        # Wait for response (with timeout)
        response_queue = f"workflow.{workflow.id}.responses"
        response = await self.message_broker.consume_message(response_queue, timeout=task.timeout)
        
        if response:
            return response.get("result")
        else:
            raise Exception("Task timeout")
    
    async def _handle_decision(self, workflow: Workflow, task: WorkflowTask) -> Any:
        """Handle decision tasks."""
        # Get result from dependent task
        if task.dependencies:
            dep_task = workflow.tasks[task.dependencies[0]]
            result = dep_task.result
            
            # Apply decision logic
            if isinstance(result, dict):
                confidence = result.get("confidence", 0.0)
                threshold = task.conditions.get("confidence_threshold", 0.8)
                
                return confidence >= threshold
        
        return True
    
    async def _handle_parallel(self, workflow: Workflow, task: WorkflowTask) -> Any:
        """Handle parallel execution."""
        # Execute all dependencies in parallel
        results = []
        for dep_id in task.dependencies:
            dep_task = workflow.tasks[dep_id]
            results.append(dep_task.result)
        
        return results
    
    async def _handle_sequence(self, workflow: Workflow, task: WorkflowTask) -> Any:
        """Handle sequence execution."""
        # Dependencies are already executed in order
        last_dep = task.dependencies[-1] if task.dependencies else None
        if last_dep:
            return workflow.tasks[last_dep].result
        
        return None
    
    async def _handle_condition(self, workflow: Workflow, task: WorkflowTask) -> Any:
        """Handle conditional tasks."""
        # Evaluate condition based on context
        condition = task.conditions.get("if")
        if condition:
            # Simple condition evaluation
            return eval(condition, {"__builtins__": {}}, workflow.context)
        
        return True
    
    def _get_ready_tasks(self, workflow: Workflow) -> List[str]:
        """Get tasks that are ready to execute."""
        ready = []
        
        for task_id, task in workflow.tasks.items():
            if task.status != WorkflowStatus.PENDING:
                continue
            
            # Check if all dependencies are complete
            deps_complete = all(
                workflow.tasks[dep].status == WorkflowStatus.COMPLETED
                for dep in task.dependencies
            )
            
            if deps_complete:
                ready.append(task_id)
        
        return ready
    
    def _is_workflow_complete(self, workflow: Workflow) -> bool:
        """Check if workflow is complete."""
        for task in workflow.tasks.values():
            if task.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING, WorkflowStatus.RETRYING]:
                return False
        return True
    
    def _is_workflow_stuck(self, workflow: Workflow) -> bool:
        """Check if workflow is stuck."""
        # Simple check - if no progress for 5 minutes, consider stuck
        if workflow.execution_history:
            last_event = workflow.execution_history[-1]["timestamp"]
            last_time = datetime.fromisoformat(last_event)
            return (datetime.now() - last_time).total_seconds() > 300
        return False
    
    def _update_performance_metrics(self, workflow: Workflow):
        """Update performance metrics for optimization."""
        duration = (workflow.completed_at - workflow.started_at).total_seconds()
        
        for task in workflow.tasks.values():
            agent = task.agent
            if agent not in self.performance_metrics:
                self.performance_metrics[agent] = {
                    "total_tasks": 0,
                    "success_rate": 0.0,
                    "avg_duration": 0.0
                }
            
            metrics = self.performance_metrics[agent]
            metrics["total_tasks"] += 1
            
            if task.status == WorkflowStatus.COMPLETED:
                task_duration = (task.completed_at - task.started_at).total_seconds()
                metrics["avg_duration"] = (metrics["avg_duration"] * (metrics["total_tasks"] - 1) + task_duration) / metrics["total_tasks"]
                metrics["success_rate"] = (metrics["success_rate"] * (metrics["total_tasks"] - 1) + 1.0) / metrics["total_tasks"]
            else:
                metrics["success_rate"] = (metrics["success_rate"] * (metrics["total_tasks"] - 1)) / metrics["total_tasks"]
    
    async def _persist_workflow(self, workflow: Workflow):
        """Persist workflow to database."""
        await self.db.cache.set(
            f"workflow:{workflow.id}",
            json.dumps({
                "id": workflow.id,
                "name": workflow.name,
                "status": workflow.status.value,
                "created_by": workflow.created_by,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "task_count": len(workflow.tasks),
                "execution_history": workflow.execution_history[-10:]  # Last 10 events
            }),
            expire=3600  # 1 hour
        )
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            # Try to get from cache
            cached = await self.db.cache.get(f"workflow:{workflow_id}")
            if cached:
                return json.loads(cached)
            return None
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_by": workflow.created_by,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "tasks": {
                task_id: {
                    "status": task.status.value,
                    "agent": task.agent,
                    "duration": (task.completed_at - task.started_at).total_seconds() if task.completed_at else None
                }
                for task_id, task in workflow.tasks.items()
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for optimization."""
        return self.performance_metrics
    
    async def optimize_workflow_routing(self):
        """Optimize agent routing based on performance metrics."""
        # This would update agent selection logic based on historical performance
        # For example, if writer is faster at certain types of tasks, route more there
        pass


# Singleton instance
_workflow_engine = None

def get_workflow_engine() -> AgentWorkflowEngine:
    """Get workflow engine instance."""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = AgentWorkflowEngine()
    return _workflow_engine
