"""FastAPI REST API for Agent Dream Team."""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime

from team_enhanced import create_enhanced_team
from database import get_postgres, get_redis
from neo4j_graph import get_knowledge_graph

# Initialize FastAPI app
app = FastAPI(
    title="Agent Dream Team API",
    description="Multi-agent AI system with enterprise infrastructure",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Pydantic Models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message to send to agents")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field("default", description="User identifier")
    stream: Optional[bool] = Field(False, description="Enable streaming response")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    handoff_count: int = Field(..., description="Number of agent handoffs")
    agents_involved: List[str] = Field(..., description="List of agents that participated")


class TaskRequest(BaseModel):
    """Async task request model."""
    task_description: str = Field(..., description="Task description")
    user_id: Optional[str] = Field("default", description="User identifier")
    priority: Optional[int] = Field(0, description="Task priority (0-9)")


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    created_at: str = Field(..., description="Task creation timestamp")


class TaskStatus(BaseModel):
    """Task status model."""
    task_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class AgentInfo(BaseModel):
    """Agent information model."""
    name: str
    role: str
    capabilities: List[str]
    status: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: Dict[str, str]


# In-memory task storage (use Redis in production)
tasks: Dict[str, Dict[str, Any]] = {}


# Dependency: Verify API key
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header."""
    # TODO: Implement proper API key verification
    # For now, accept any bearer token
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials


# Health check
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API and service health."""
    services = {}
    
    # Check PostgreSQL
    try:
        db = get_postgres()
        db.connect()
        services["postgresql"] = "healthy"
    except Exception as e:
        services["postgresql"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        cache = get_redis()
        cache.client.ping()
        services["redis"] = "healthy"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)}"
    
    # Check Neo4j
    try:
        kg = get_knowledge_graph()
        services["neo4j"] = "healthy"
    except Exception as e:
        services["neo4j"] = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": services
    }


# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """Send a message to the agent team and get a response."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create agent team
        team, memory = create_enhanced_team()
        
        # Execute task
        result = team(request.message)
        
        # Extract response
        response_text = ""
        if result.results and result.node_history:
            last_node_id = result.node_history[-1].node_id
            if last_node_id in result.results:
                node_result = result.results[last_node_id]
                if hasattr(node_result.result, 'message'):
                    message = node_result.result.message
                    if message and "content" in message:
                        for content_block in message["content"]:
                            if "text" in content_block:
                                response_text += content_block["text"]
        
        # Get agents involved
        agents_involved = [node.node_id for node in result.node_history]
        
        # Save to database
        db = get_postgres()
        db.save_conversation(
            session_id=session_id,
            user_message=request.message,
            agent_response=response_text,
            metadata={
                "execution_time_ms": result.execution_time,
                "handoff_count": len(result.node_history),
                "agents_involved": agents_involved
            }
        )
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            execution_time_ms=result.execution_time,
            handoff_count=len(result.node_history),
            agents_involved=agents_involved
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Streaming chat endpoint
@app.post("/api/chat/stream", tags=["Chat"])
async def chat_stream(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """Stream agent responses in real-time."""
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            team, memory = create_enhanced_team()
            
            # Stream events
            async for event in team.stream_async(request.message):
                yield f"data: {json.dumps(event)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


# Get conversation history
@app.get("/api/chat/history/{session_id}", tags=["Chat"])
async def get_history(
    session_id: str,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """Get conversation history for a session."""
    try:
        db = get_postgres()
        history = db.get_conversation_history(session_id, limit)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List agents
@app.get("/api/agents", response_model=List[AgentInfo], tags=["Agents"])
async def list_agents(api_key: str = Depends(verify_api_key)):
    """List all available agents."""
    return [
        AgentInfo(
            name="coordinator",
            role="Task Coordinator",
            capabilities=["task_analysis", "delegation", "synthesis"],
            status="active"
        ),
        AgentInfo(
            name="researcher",
            role="Research Specialist",
            capabilities=["research", "analysis", "data_gathering"],
            status="active"
        ),
        AgentInfo(
            name="writer",
            role="Content Writer",
            capabilities=["writing", "formatting", "documentation"],
            status="active"
        ),
        AgentInfo(
            name="reviewer",
            role="Quality Reviewer",
            capabilities=["review", "quality_check", "feedback"],
            status="active"
        )
    ]


# Get agent statistics
@app.get("/api/agents/{agent_name}/stats", tags=["Agents"])
async def get_agent_stats(
    agent_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Get statistics for a specific agent."""
    try:
        kg = get_knowledge_graph()
        stats = kg.get_agent_stats(agent_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create async task
@app.post("/api/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create an asynchronous task."""
    task_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    # Store task
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "description": request.task_description,
        "user_id": request.user_id,
        "created_at": created_at,
        "result": None,
        "error": None
    }
    
    # Add to background tasks
    background_tasks.add_task(execute_task, task_id, request.task_description)
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        created_at=created_at
    )


# Get task status
@app.get("/api/tasks/{task_id}", response_model=TaskStatus, tags=["Tasks"])
async def get_task_status(
    task_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get the status of an async task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatus(**tasks[task_id])


# Background task execution
async def execute_task(task_id: str, task_description: str):
    """Execute a task in the background."""
    try:
        tasks[task_id]["status"] = "running"
        
        # Create team and execute
        team, memory = create_enhanced_team()
        result = team(task_description)
        
        # Extract result
        response_text = ""
        if result.results and result.node_history:
            last_node_id = result.node_history[-1].node_id
            if last_node_id in result.results:
                node_result = result.results[last_node_id]
                if hasattr(node_result.result, 'message'):
                    message = node_result.result.message
                    if message and "content" in message:
                        for content_block in message["content"]:
                            if "text" in content_block:
                                response_text += content_block["text"]
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = response_text
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["completed_at"] = datetime.now().isoformat()


# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time bidirectional communication."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create team
            team, memory = create_enhanced_team()
            
            # Stream response
            async for event in team.stream_async(message_data.get("message", "")):
                await websocket.send_json(event)
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "name": "Agent Dream Team API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
