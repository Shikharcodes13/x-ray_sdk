from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class RuleDefinition(BaseModel):
    rule_id: str
    description: str
    operator: str
    value: Any
    source: str = "config"


class Evaluation(BaseModel):
    entity_id: str
    value: Any
    passed: bool
    reason: str


class StepOutput(BaseModel):
    passed: Optional[int] = None
    failed: Optional[int] = None
    selected_ids: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None


class Step(BaseModel):
    step_id: str
    execution_id: str
    name: str
    type: str = "default"
    input: Dict[str, Any] = {}
    rules: List[RuleDefinition] = []
    evaluations: List[Evaluation] = []
    output: StepOutput = StepOutput()
    started_at: datetime
    ended_at: Optional[datetime] = None


class ExecutionMetadata(BaseModel):
    environment: Optional[str] = None
    trigger: Optional[str] = None
    user: Optional[str] = None
    version: Optional[str] = None


class Execution(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: str = "running"  # running, completed, failed
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    metadata: ExecutionMetadata = ExecutionMetadata()
    steps: List[Step] = []


class CreateExecutionRequest(BaseModel):
    name: str
    metadata: Optional[ExecutionMetadata] = None


class CreateStepRequest(BaseModel):
    name: str
    type: str = "default"
    input: Dict[str, Any] = {}
    rules: List[RuleDefinition] = []


class CreateEvaluationRequest(BaseModel):
    entity_id: str
    value: Any
    passed: bool
    reason: str


class UpdateStepRequest(BaseModel):
    output: Optional[Dict[str, Any]] = None
    ended_at: Optional[datetime] = None

