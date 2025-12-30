"""
X-Ray SDK Data Models (Optional)

These models are OPTIONAL helpers for type safety and validation.
The SDK works perfectly fine with plain dictionaries - these models are just
convenience helpers for users who want validation.

IMPORTANT: The SDK is designed to work with ANY backend that implements the
API contract. These models are NOT required - you can:
1. Use plain dicts (SDK works as-is)
2. Use these models for validation (optional)
3. Disable validation: XRay(..., validate_requests=False)
4. Use your own models that match the API contract

The SDK will send whatever data you provide to the backend, which will
validate it according to its own models.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RuleDefinition(BaseModel):
    """Rule definition for a step."""
    rule_id: str
    description: str
    operator: str
    value: Any
    source: str = "config"


class Evaluation(BaseModel):
    """Evaluation result for an entity."""
    entity_id: str
    value: Any
    passed: bool
    reason: str


class StepOutput(BaseModel):
    """Output data for a step."""
    passed: Optional[int] = None
    failed: Optional[int] = None
    selected_ids: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None


class ExecutionMetadata(BaseModel):
    """Metadata for an execution."""
    environment: Optional[str] = None
    trigger: Optional[str] = None
    user: Optional[str] = None
    version: Optional[str] = None


# Request models (what SDK sends to backend)
class CreateExecutionRequest(BaseModel):
    """Request to create a new execution."""
    name: str
    metadata: Optional[ExecutionMetadata] = None


class CreateStepRequest(BaseModel):
    """Request to create a new step."""
    name: str
    type: str = "default"
    input: Dict[str, Any] = {}
    rules: List[RuleDefinition] = []


class CreateEvaluationRequest(BaseModel):
    """Request to add an evaluation."""
    entity_id: str
    value: Any
    passed: bool
    reason: str


class UpdateStepRequest(BaseModel):
    """Request to update a step."""
    output: Optional[Dict[str, Any]] = None
    ended_at: Optional[datetime] = None


# Response models (what SDK receives from backend)
class ExecutionResponse(BaseModel):
    """Response model for execution."""
    execution_id: str
    name: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    metadata: ExecutionMetadata = ExecutionMetadata()
    steps: List[Any] = []  # Steps are complex, handled separately


class StepResponse(BaseModel):
    """Response model for step."""
    step_id: str
    execution_id: str
    name: str
    type: str
    input: Dict[str, Any]
    rules: List[RuleDefinition]
    evaluations: List[Evaluation]
    output: StepOutput
    started_at: datetime
    ended_at: Optional[datetime] = None

