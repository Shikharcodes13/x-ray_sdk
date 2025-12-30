from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
from uuid import uuid4

try:
    from .models import (
        Execution, Step, CreateExecutionRequest, CreateStepRequest,
        CreateEvaluationRequest, UpdateStepRequest, StepOutput, ExecutionMetadata, Evaluation
    )
    from .storage import storage
except ImportError:
    from backend.models import (
        Execution, Step, CreateExecutionRequest, CreateStepRequest,
        CreateEvaluationRequest, UpdateStepRequest, StepOutput, ExecutionMetadata, Evaluation
    )
    from backend.storage import storage

app = FastAPI(title="X-Ray Debugging System", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/executions", response_model=Execution)
async def create_execution(request: CreateExecutionRequest):
    """Create a new execution."""
    execution = Execution(
        name=request.name,
        metadata=request.metadata or ExecutionMetadata()
    )
    return storage.create_execution(execution)


@app.get("/api/executions", response_model=List[Execution])
async def list_executions(limit: int = 100):
    """List all executions."""
    return storage.list_executions(limit=limit)


@app.get("/api/executions/{execution_id}", response_model=Execution)
async def get_execution(execution_id: str):
    """Get a specific execution with all its steps."""
    execution = storage.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@app.patch("/api/executions/{execution_id}")
async def update_execution(execution_id: str, status: str = None, ended_at: datetime = None):
    """Update execution status."""
    updates = {}
    if status:
        updates["status"] = status
    if ended_at:
        updates["ended_at"] = ended_at
    
    execution = storage.update_execution(execution_id, **updates)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@app.post("/api/executions/{execution_id}/steps", response_model=Step)
async def create_step(execution_id: str, request: CreateStepRequest):
    """Create a new step in an execution."""
    execution = storage.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    step = Step(
        step_id=str(uuid4()),
        execution_id=execution_id,
        name=request.name,
        type=request.type,
        input=request.input,
        rules=request.rules,
        started_at=datetime.utcnow()
    )
    return storage.add_step(execution_id, step)


@app.get("/api/executions/{execution_id}/steps", response_model=List[Step])
async def list_steps(execution_id: str):
    """List all steps for an execution."""
    execution = storage.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution.steps


@app.get("/api/steps/{step_id}", response_model=Step)
async def get_step(step_id: str):
    """Get a specific step."""
    step = storage.get_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return step


@app.patch("/api/steps/{step_id}", response_model=Step)
async def update_step(step_id: str, request: UpdateStepRequest):
    """Update a step (typically to add output and end time)."""
    updates = {}
    if request.output:
        updates["output"] = StepOutput(**request.output)
    if request.ended_at:
        updates["ended_at"] = request.ended_at
    else:
        updates["ended_at"] = datetime.utcnow()
    
    step = storage.update_step(step_id, **updates)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return step


@app.post("/api/steps/{step_id}/evaluations", response_model=Step)
async def add_evaluation(step_id: str, request: CreateEvaluationRequest):
    """Add an evaluation to a step."""
    step = storage.get_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    evaluation = Evaluation(
        entity_id=request.entity_id,
        value=request.value,
        passed=request.passed,
        reason=request.reason
    )
    step.evaluations.append(evaluation)
    return step


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

