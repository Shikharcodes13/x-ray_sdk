# X-Ray SDK System Design

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [API Contract](#api-contract)
6. [Integration Patterns](#integration-patterns)
7. [Data Models](#data-models)
8. [Design Principles](#design-principles)
9. [Scalability & Performance](#scalability--performance)
10. [Error Handling](#error-handling)
11. [Security Considerations](#security-considerations)

---

## Overview

X-Ray is a debugging and execution tracking system designed to answer **"Why did the system make this decision?"** rather than just "What happened?". It provides step-by-step execution tracking with entity-level evaluations and reasoning capture.

### Key Characteristics
- **SDK-First Design**: The SDK is the primary component, independent of backend implementation
- **Backend Agnostic**: Works with any backend implementing the API contract
- **Reasoning as First-Class Citizen**: Every evaluation includes a `reason` field
- **Entity-Level Tracking**: Tracks individual entities through pipelines, not just aggregates
- **General-Purpose**: Domain-agnostic, works for any multi-step decision process

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application Code                     │
│  (LLM workflows, search systems, recommendation engines)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ imports SDK
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      X-Ray SDK (sdk/)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Core Components:                                     │   │
│  │  • XRay Client (HTTP client)                          │   │
│  │  • StepContext (Context manager)                      │   │
│  │  • trace_function (Decorator)                         │   │
│  │  • StepRunner (Data-driven execution)                 │   │
│  │                        
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP REST API
                       │ (JSON over HTTP)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dashboard Backend API (backend/)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Server (Reference Implementation)            │   │
│  │  • REST Endpoints (API Contract)                      │   │
│  │  • Request Validation (Pydantic)                       │   │
│  │  • CORS Middleware                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Storage Layer (storage.py)                            │   │
│  │  • InMemoryStorage (Development)                       │   │
│  │  • Replaceable with Database (PostgreSQL, MongoDB)    │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Serves data via API
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Frontend Dashboard (frontend/)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React + Vite Application                             │   │
│  │  • Execution List View                                │   │
│  │  • Execution Detail View                              │   │
│  │  • Timeline Visualization                             │   │
│  │  • Step Viewer (Evaluations, Input/Output)            │   │
│  │                                    
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### 1. SDK (`sdk/`)
**Purpose**: Client library that users import into their code

**Responsibilities**:
- Track execution lifecycle (start/end)
- Manage step lifecycle (start/end)
- Record evaluations with reasoning
- Make HTTP requests to backend
- Provide convenient APIs (context managers, decorators)
- Optional request validation

**Key Design**:
- Zero backend dependencies
- Pure HTTP client
- Works with any backend implementing API contract
- Optional models for validation (can use plain dicts)

#### 2. Backend (`backend/`)
**Purpose**: Server that receives and stores execution data

**Responsibilities**:
- Implement API contract (REST endpoints)
- Validate incoming requests
- Store execution data
- Serve data to frontend
- Handle CORS for frontend

**Key Design**:
- Reference implementation (can be replaced)
- API contract is the interface
- Storage layer is pluggable
- FastAPI for async performance

#### 3. Frontend (`frontend/`)
**Purpose**: Dashboard UI to visualize executions

**Responsibilities**:
- Display execution list
- Show execution timeline
- Display step details and evaluations
- Filter and search capabilities
- Real-time updates via polling

---

## Component Design

### SDK Core Components

#### 1. XRay Client (`XRay` class)

```python
class XRay:
    """
    Main client for tracking executions, steps, and evaluations.
    
    State Management:
    - execution_id: Current execution being tracked
    - current_step_id: Current step being tracked
    
    Configuration:
    - api_url: Backend API endpoint
    - timeout: HTTP request timeout
    - validate_requests: Enable/disable request validation
    """
```

**Key Methods**:
- `start_execution(metadata)` → Creates execution, returns execution_id
- `start_step(name, type, input_data, rules)` → Creates step, returns step_id
- `record_evaluation(entity_id, value, passed, reason)` → Records evaluation
- `end_step(output)` → Closes step, sets output
- `end_execution(status)` → Closes execution

**Design Patterns**:
- **Stateful Client**: Maintains execution_id and step_id internally
- **HTTP Client**: Uses `requests` library for API calls
- **Error Handling**: Raises `XRayError` on failures
- **Optional Validation**: Can validate requests using models or send raw dicts

#### 2. StepContext (Context Manager)

```python
class StepContext:
    """
    Enhanced context manager for steps with helper methods.
    
    Provides:
    - Automatic step start/end
    - Convenient evaluation methods
    - Output management
    - Error handling
    """
```

**Usage Pattern**:
```python
with step(xray, "Filter Candidates", step_type="filter") as step_ctx:
    step_ctx.evaluate(entity_id="item_1", value=4.5, condition=True, reason="Rating >= 4.0")
    step_ctx.set_output({"passed": 3, "failed": 2})
```

**Benefits**:
- Automatic step lifecycle management
- Exception handling (errors captured in output)
- Cleaner code (no manual start/end calls)

#### 3. trace_function (Decorator)

```python
def trace_function(xray, step_type, extract_input, extract_output, extract_evaluations):
    """
    Decorator to automatically trace function execution.
    
    Allows wrapping existing functions without code modification.
    """
```

**Usage Pattern**:
```python
@trace_function(xray, step_type="filter")
def filter_candidates(candidates, min_rating):
    return [c for c in candidates if c['rating'] >= min_rating]
```

**Benefits**:
- Non-invasive instrumentation
- Works with existing code
- Configurable input/output extraction

#### 4. StepRunner (Data-Driven Execution)

```python
class StepRunner:
    """
    Generic step runner for configuration-based execution.
    
    Enables data-driven pipelines where steps are defined in config.
    """
```

**Usage Pattern**:
```python
runner = StepRunner(xray)
runner.register_handler("filter", filter_handler)
runner.register_handler("rank", rank_handler)

pipeline = [
    {"name": "Filter", "type": "filter", "input": {...}},
    {"name": "Rank", "type": "rank", "input": {...}}
]
outputs = runner.execute_pipeline(pipeline)
```

**Benefits**:
- Configuration-driven execution
- Reusable step handlers
- Easy to test and modify

---

## Data Flow

### Execution Lifecycle

```
1. User Code
   │
   ├─> xray = XRay("execution_name", api_url="...")
   │
   ├─> xray.start_execution(metadata={...})
   │   │
   │   └─> HTTP POST /api/executions
   │       └─> Backend creates Execution
   │           └─> Returns execution_id
   │
   ├─> xray.start_step(name="Step 1", ...)
   │   │
   │   └─> HTTP POST /api/executions/{id}/steps
   │       └─> Backend creates Step
   │           └─> Returns step_id
   │
   ├─> xray.record_evaluation(...)  (multiple times)
   │   │
   │   └─> HTTP POST /api/steps/{id}/evaluations
   │       └─> Backend appends Evaluation to Step
   │
   ├─> xray.end_step(output={...})
   │   │
   │   └─> HTTP PATCH /api/steps/{id}
   │       └─> Backend updates Step (output, ended_at)
   │
   └─> xray.end_execution(status="completed")
       │
       └─> HTTP PATCH /api/executions/{id}
           └─> Backend updates Execution (status, ended_at)
```

### Frontend Data Flow

```
Frontend (React)
   │
   ├─> GET /api/executions
   │   └─> Backend returns list of executions
   │       └─> Frontend displays execution list
   │
   ├─> GET /api/executions/{id}
   │   └─> Backend returns execution with all steps
   │       └─> Frontend displays timeline and details
   │
   └─> Polling (every 2 seconds for active executions)
       └─> GET /api/executions/{id}
           └─> Updates UI with latest data
```

---

## API Contract

The API contract defines the interface between SDK and backend. Any backend implementing these endpoints will work with the SDK.

### Required Endpoints

#### 1. Create Execution
```
POST /api/executions
Request: {
  "name": string,
  "metadata": object (optional)
}
Response: {
  "execution_id": string,
  "name": string,
  "status": "running",
  "started_at": datetime,
  ...
}
```

#### 2. Create Step
```
POST /api/executions/{execution_id}/steps
Request: {
  "name": string,
  "type": string,
  "input": object,
  "rules": array (optional)
}
Response: {
  "step_id": string,
  "execution_id": string,
  "name": string,
  "type": string,
  "started_at": datetime,
  ...
}
```

#### 3. Add Evaluation
```
POST /api/steps/{step_id}/evaluations
Request: {
  "entity_id": string,
  "value": any,
  "passed": boolean,
  "reason": string
}
Response: Step object (with updated evaluations)
```

#### 4. Update Step
```
PATCH /api/steps/{step_id}
Request: {
  "output": object (optional),
  "ended_at": datetime (optional)
}
Response: Step object (with updated output and ended_at)
```

#### 5. Update Execution
```
PATCH /api/executions/{execution_id}
Request: {
  "status": string (optional),
  "ended_at": datetime (optional)
}
Response: Execution object (with updated status and ended_at)
```

#### 6. List Executions
```
GET /api/executions?limit=100
Response: Array of Execution objects
```

#### 7. Get Execution
```
GET /api/executions/{execution_id}
Response: Execution object with all steps and evaluations
```

---

## Integration Patterns

### Pattern 1: Direct Code Integration

**Description**: Manual instrumentation with explicit SDK calls

**Use Case**: Full control over what to track, custom logic

```python
xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution(metadata={"environment": "prod"})

xray.start_step("Filter", step_type="filter", input_data={"min_rating": 4.0})
for candidate in candidates:
    passed = candidate.rating >= 4.0
    xray.record_evaluation(
        entity_id=candidate.id,
        value=candidate.rating,
        passed=passed,
        reason=f"Rating {candidate.rating} >= 4.0" if passed else f"Rating {candidate.rating} < 4.0"
    )
xray.end_step(output={"passed": 3, "failed": 2})

xray.end_execution(status="completed")
```

### Pattern 2: Context Manager Integration

**Description**: Using `step()` context manager for cleaner code

**Use Case**: Preferred pattern for most use cases

```python
xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution()

with step(xray, "Filter Candidates", step_type="filter", 
          input_data={"min_rating": 4.0}) as step_ctx:
    for candidate in candidates:
        step_ctx.evaluate(
            entity_id=candidate.id,
            value=candidate.rating,
            condition=candidate.rating >= 4.0,
            reason=f"Rating {candidate.rating} >= 4.0"
        )
    step_ctx.set_output({"passed": 3, "failed": 2})

xray.end_execution(status="completed")
```

### Pattern 3: Decorator Integration (Adapter Mode)

**Description**: Wrapping existing functions with decorators

**Use Case**: Instrument existing code without modification

```python
xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution()

@trace_function(xray, step_type="filter")
def filter_candidates(candidates, min_rating):
    return [c for c in candidates if c['rating'] >= min_rating]

filtered = filter_candidates(candidates, min_rating=4.0)

xray.end_execution(status="completed")
```

### Pattern 4: Data-Driven Integration

**Description**: Configuration-based pipeline execution

**Use Case**: Dynamic pipelines, A/B testing, configuration-driven systems

```python
xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution()

runner = StepRunner(xray)
runner.register_handler("filter", filter_handler)
runner.register_handler("rank", rank_handler)

pipeline_config = [
    {
        "name": "Filter by Rating",
        "type": "filter",
        "input": {"candidates": candidates, "min_rating": 4.0}
    },
    {
        "name": "Rank by Score",
        "type": "rank",
        "input": {"candidates": filtered_candidates}
    }
]

outputs = runner.execute_pipeline(pipeline_config)
xray.end_execution(status="completed")
```

---

## Data Models

### Core Entities

#### Execution
```python
{
    "execution_id": "uuid",
    "name": "string",
    "status": "running" | "completed" | "failed",
    "started_at": datetime,
    "ended_at": datetime | null,
    "metadata": {
        "environment": "string",
        "trigger": "string",
        "user": "string",
        "version": "string"
    },
    "steps": [Step]
}
```

#### Step
```python
{
    "step_id": "uuid",
    "execution_id": "uuid",
    "name": "string",
    "type": "filter" | "rank" | "transform" | "select" | "default",
    "input": object,
    "rules": [RuleDefinition],
    "evaluations": [Evaluation],
    "output": {
        "passed": int,
        "failed": int,
        "selected_ids": [string],
        "data": object
    },
    "started_at": datetime,
    "ended_at": datetime | null
}
```

#### Evaluation
```python
{
    "entity_id": "string",
    "value": any,
    "passed": boolean,
    "reason": "string"  // Critical: explains WHY
}
```

#### RuleDefinition
```python
{
    "rule_id": "string",
    "description": "string",
    "operator": "string",
    "value": any,
    "source": "config" | "code" | "user"
}
```

---

## Design Principles

### 1. SDK Independence
- SDK has zero dependencies on backend implementation
- Works with any backend implementing the API contract
- Can be used with Node.js, Go, Java backends

### 2. Backend Replaceability
- Backend is a reference implementation
- Storage layer is pluggable (in-memory → database)
- API contract is the only requirement

### 3. Optional Validation
- Models are optional helpers
- SDK works with plain dictionaries
- Validation can be disabled: `XRay(..., validate_requests=False)`
- Backend validates according to its own models

### 4. Reasoning as First-Class Citizen
- Every evaluation includes a `reason` field
- This is the core differentiator from traditional tracing
- Enables answering "why" questions

### 5. Entity-Level Tracking
- Tracks individual entities (candidates, products, etc.)
- Not just aggregate metrics
- See exactly why each item passed or failed

### 6. General-Purpose Design
- SDK doesn't know about specific domains
- Just tracks executions, steps, and evaluations
- Reusable across any domain

### 7. Multiple Integration Modes
- Direct code integration
- Adapter mode (decorators)
- Data-driven mode (configuration)
- Accommodates different codebases and workflows

---

## Scalability & Performance

### Current Implementation (Development)

**Limitations**:
- In-memory storage (data lost on restart)
- Synchronous HTTP requests
- No batching of evaluations
- Polling-based frontend updates

### Production Considerations

#### 1. Storage Layer
- **Replace** `InMemoryStorage` with database:
  - PostgreSQL (relational, ACID)
  - MongoDB (document-based, flexible)
  - Redis (caching layer)
- **Add** data retention policies (TTL, archival)
- **Implement** pagination for large result sets

#### 2. API Performance
- **Add** request batching for evaluations
- **Implement** async processing for heavy operations
- **Add** caching layer (Redis) for frequently accessed executions
- **Consider** GraphQL for flexible queries

#### 3. Frontend Updates
- **Replace** polling with WebSockets for real-time updates
- **Implement** incremental updates (only changed data)
- **Add** virtual scrolling for large execution lists

#### 4. SDK Performance
- **Add** local buffering for evaluations (batch send)
- **Implement** async HTTP client (aiohttp)
- **Add** retry logic with exponential backoff
- **Consider** offline mode (queue requests when backend unavailable)

#### 5. Horizontal Scaling
- **Stateless** backend (can scale horizontally)
- **Shared** storage (database, not in-memory)
- **Load balancer** for multiple backend instances
- **Message queue** for async processing (RabbitMQ, Kafka)

---

## Error Handling

### SDK Error Handling

```python
class XRayError(Exception):
    """Base exception for X-Ray SDK errors."""
    pass
```

**Error Scenarios**:
1. **Network Errors**: Connection timeout, DNS failure
   - Raises `XRayError` with original exception
   - User can catch and handle gracefully

2. **API Errors**: 4xx/5xx responses
   - `response.raise_for_status()` raises HTTPError
   - Wrapped in `XRayError` for consistent interface

3. **Validation Errors**: Invalid request data
   - If validation enabled: raises validation error
   - If validation disabled: backend validates and returns error

4. **State Errors**: Invalid operation sequence
   - `ValueError` for missing execution/step
   - Clear error messages guide correct usage

### Backend Error Handling

- **404**: Execution/Step not found
- **400**: Invalid request data
- **500**: Internal server error
- **CORS**: Handled by middleware

### Frontend Error Handling

- **Network Errors**: Display error message, retry button
- **API Errors**: Show error details, allow refresh
- **Polling Errors**: Continue polling, show warning

---

## Security Considerations

### Current Implementation (Development)

**No Security Features**:
- No authentication
- No authorization
- No rate limiting
- No input sanitization beyond Pydantic validation

### Production Security Requirements

#### 1. Authentication
- **API Keys**: Simple authentication for SDK
- **OAuth 2.0**: For user-facing applications
- **JWT Tokens**: Stateless authentication
- **Service Accounts**: For service-to-service communication

#### 2. Authorization
- **User Isolation**: Users can only see their executions
- **Role-Based Access**: Admin, viewer, editor roles
- **Execution-Level Permissions**: Share specific executions

#### 3. Input Validation
- **Pydantic Models**: Already implemented
- **Sanitization**: Clean user inputs
- **Size Limits**: Max request size, max evaluations per step

#### 4. Rate Limiting
- **Per-User Limits**: Prevent abuse
- **Per-API-Key Limits**: Control usage
- **Throttling**: Graceful degradation

#### 5. Data Privacy
- **Encryption at Rest**: Encrypt stored data
- **Encryption in Transit**: HTTPS only
- **PII Handling**: Mask sensitive data in evaluations
- **Data Retention**: Automatic deletion of old data

#### 6. Network Security
- **HTTPS Only**: Enforce TLS
- **CORS Configuration**: Restrict allowed origins
- **IP Whitelisting**: Optional for enterprise deployments

---

## Summary

The X-Ray SDK is designed with the following key principles:

1. **SDK-First**: The SDK is the main component, independent and distributable
2. **Backend Agnostic**: Works with any backend implementing the API contract
3. **Reasoning Focus**: Captures "why" decisions were made, not just "what" happened
4. **Entity-Level**: Tracks individual entities through pipelines
5. **General-Purpose**: Domain-agnostic, reusable across any use case
6. **Multiple Integration Modes**: Accommodates different codebases and workflows
7. **Optional Validation**: Flexible validation, works with plain dicts or models

The architecture is designed for:
- **Development**: Quick setup, in-memory storage, simple deployment
- **Production**: Replaceable storage, scalable backend, secure API, real-time updates

The system can scale from a single developer debugging a script to an enterprise-grade execution tracking system with proper storage, security, and performance optimizations.


