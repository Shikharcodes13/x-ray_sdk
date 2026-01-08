# X-Ray Data Models & Design Rationale

## Overview

X-Ray uses a hierarchical data model: **Execution → Steps → Evaluations**. This design captures the complete decision trail while remaining general-purpose and domain-agnostic.

## Core Data Models

### 1. Execution

```python
class Execution(BaseModel):
    execution_id: str                    # Unique identifier (UUID)
    name: str                            # Human-readable name
    status: str                          # "running", "completed", "failed"
    started_at: datetime                 # When execution started
    ended_at: Optional[datetime]         # When execution ended
    metadata: ExecutionMetadata          # Custom metadata
    steps: List[Step]                    # All steps in this execution
```

**Design Rationale:**
- **Top-level container** - Represents one complete run of a pipeline
- **Status tracking** - Allows tracking of in-progress executions
- **Metadata** - Flexible field for environment, user, version, etc.
- **Steps list** - Contains all steps in chronological order

**Why this structure?**
- One execution = one complete decision process
- Status allows real-time tracking (dashboard can poll for updates)
- Metadata provides context without being domain-specific
- Steps are nested, not separate, to maintain execution context

---

### 2. Step

```python
class Step(BaseModel):
    step_id: str                         # Unique identifier (UUID)
    execution_id: str                    # Parent execution
    name: str                            # Human-readable name
    type: str                            # "filter", "rank", "transform", etc.
    input: Dict[str, Any]                # Input data (flexible)
    rules: List[RuleDefinition]          # Rules applied in this step
    evaluations: List[Evaluation]        # All entity evaluations
    output: StepOutput                   # Output data
    started_at: datetime                 # When step started
    ended_at: Optional[datetime]         # When step ended
```

**Design Rationale:**
- **Represents one decision point** - Each step is a logical unit of work
- **Type field** - Allows categorization (filter, rank, transform, select)
- **Input/Output** - Flexible Dict[str, Any] - works for any domain
- **Rules** - Documents what rules were applied (for transparency)
- **Evaluations** - Entity-level tracking (the core of X-Ray)
- **Timestamps** - Performance tracking

**Why this structure?**
- Steps are the building blocks - each one makes decisions
- Type helps dashboard categorize and visualize
- Input/Output as Dict allows any data structure (not tied to domain)
- Rules provide transparency - you can see what criteria were used
- Evaluations are the key - they show WHY decisions were made

---

### 3. Evaluation

```python
class Evaluation(BaseModel):
    entity_id: str                       # Unique identifier for entity
    value: Any                           # The value being evaluated
    passed: bool                         # Did it pass or fail?
    reason: str                          # WHY it passed/failed (KEY FIELD)
```

**Design Rationale:**
- **Entity-level tracking** - Each candidate/product/item is tracked individually
- **Value field** - Can be anything (number, string, object) - flexible
- **Passed boolean** - Simple pass/fail for filtering
- **Reason string** - **This is the core differentiator** - explains WHY

**Why this structure?**
- **Entity-level is crucial** - You need to see why EACH item passed/failed
- **Value is Any** - Works for ratings, prices, complex objects, etc.
- **Reason is required** - This is what makes X-Ray different from traditional tracing
- **Simple structure** - Easy to understand and query

**Example:**
```python
Evaluation(
    entity_id="flight_AI868",
    value=42220,
    passed=False,
    reason="Price Rs. 42,220 > Rs. 40,000 budget limit"
)
```

---

### 4. RuleDefinition

```python
class RuleDefinition(BaseModel):
    rule_id: str                         # Unique rule identifier
    description: str                    # Human-readable description
    operator: str                        # ">=", "<=", "==", "contains", etc.
    value: Any                           # Rule value/threshold
    source: str                          # "config", "user", "system", etc.
```

**Design Rationale:**
- **Documents rules** - Makes it clear what criteria were applied
- **Operator + Value** - Flexible enough for various rule types
- **Source** - Tracks where rule came from (config file, user input, etc.)

**Why this structure?**
- **Transparency** - You can see exactly what rules were applied
- **Flexible** - Operator can be any string (">=", "contains", "in_range", etc.)
- **Source tracking** - Helps debug where rules came from

**Example:**
```python
RuleDefinition(
    rule_id="budget_constraint",
    description="Flight price must be under Rs. 40,000",
    operator="<=",
    value=40000,
    source="config"
)
```

---

### 5. StepOutput

```python
class StepOutput(BaseModel):
    passed: Optional[int] = None         # Count of items that passed
    failed: Optional[int] = None         # Count of items that failed
    selected_ids: Optional[List[str]]    # IDs of selected items
    data: Optional[Dict[str, Any]]       # Additional output data
```

**Design Rationale:**
- **Common fields** - Passed/failed counts are common across steps
- **Selected IDs** - For selection steps, tracks what was chosen
- **Data field** - Flexible for any additional output

**Why this structure?**
- **Common patterns** - Most steps have pass/fail counts
- **Selected IDs** - Important for selection steps
- **Data is flexible** - Can store anything else needed

---

### 6. ExecutionMetadata

```python
class ExecutionMetadata(BaseModel):
    environment: Optional[str] = None    # "production", "staging", etc.
    trigger: Optional[str] = None        # "manual", "scheduled", "webhook"
    user: Optional[str] = None           # User who triggered it
    version: Optional[str] = None       # Code version
```

**Design Rationale:**
- **Common metadata** - These fields are useful across domains
- **All optional** - Not required, but helpful when available
- **Extensible** - Can add more fields as needed

**Why this structure?**
- **Standard fields** - Environment, user, version are common needs
- **Optional** - Doesn't force users to provide metadata
- **Can extend** - Users can add custom fields via Dict if needed

---

## Request/Response Models

### Request Models (SDK → Backend)

```python
CreateExecutionRequest:
    name: str
    metadata: Optional[ExecutionMetadata]

CreateStepRequest:
    name: str
    type: str = "default"
    input: Dict[str, Any] = {}
    rules: List[RuleDefinition] = []

CreateEvaluationRequest:
    entity_id: str
    value: Any
    passed: bool
    reason: str

UpdateStepRequest:
    output: Optional[Dict[str, Any]]
    ended_at: Optional[datetime]
```

**Design Rationale:**
- **Separate from domain models** - Requests are what SDK sends
- **Minimal required fields** - Only what's needed to create
- **Flexible input/output** - Dict[str, Any] allows any structure

---

## Key Design Decisions

### 1. Why Hierarchical? (Execution → Step → Evaluation)

**Decision:** Three-level hierarchy

**Rationale:**
- **Execution** = One complete pipeline run
- **Step** = One decision point (filter, rank, etc.)
- **Evaluation** = One entity checked in that step

**Benefits:**
- Clear structure - easy to understand
- Scalable - can have many steps, each with many evaluations
- Queryable - can filter by execution, step, or evaluation

**Alternative considered:** Flat structure with just evaluations
- **Rejected because:** Lost context of which step, harder to understand flow

---

### 2. Why Flexible Dict[str, Any] for Input/Output?

**Decision:** Use `Dict[str, Any]` instead of strict schemas

**Rationale:**
- **General-purpose** - Works for any domain
- **No schema enforcement** - Users can structure data however they want
- **Backend validates** - Backend can validate according to its own rules

**Benefits:**
- Works for flights, products, candidates, quotes, etc.
- No need to define schemas for each domain
- Backend can add validation if needed

**Trade-off:**
- Less type safety (but models are optional helpers)
- Backend must validate (but that's fine - backend knows its domain)

---

### 3. Why Entity-Level Evaluations?

**Decision:** Track each entity individually, not just aggregates

**Rationale:**
- **Core X-Ray principle** - Need to see WHY each item passed/failed
- **Debugging requirement** - "Why was product X excluded?" needs entity-level data
- **Transparency** - Shows the complete decision trail

**Benefits:**
- Can see exactly why each candidate/product passed or failed
- Can filter to see only failures
- Can trace a specific entity through the pipeline

**Alternative considered:** Just aggregate counts
- **Rejected because:** Lost the "why" - can't see individual decisions

---

### 4. Why Reason Field is Required?

**Decision:** `reason` is a required string field in Evaluation

**Rationale:**
- **Core differentiator** - This is what makes X-Ray different from tracing
- **Debugging essential** - "Failed" is useless, "Failed: Price $8.99 < $12.50" is useful
- **Human-readable** - Should explain in plain language

**Benefits:**
- Immediately see why decisions were made
- No need to reverse-engineer from values
- Can search/filter by reason text

**Example of good reason:**
```
"Price Rs. 42,220 > Rs. 40,000 budget limit"
```

**Example of bad reason:**
```
"Failed"
```

---

### 5. Why Optional Models in SDK?

**Decision:** Models are optional - SDK works with plain dicts

**Rationale:**
- **Plug-and-play** - SDK must work with any backend
- **No forced dependencies** - Backend might use different validation
- **Flexibility** - Users can use models or not

**Benefits:**
- SDK works with any backend implementing API contract
- Users can disable validation for custom backends
- Models are helpers, not requirements

**Implementation:**
- SDK tries to import models
- If unavailable, falls back to dicts
- Validation can be disabled: `XRay(..., validate_requests=False)`

---

### 6. Why Separate Request/Response Models?

**Decision:** Separate models for requests vs. domain objects

**Rationale:**
- **Request models** - What SDK sends (minimal, creation-focused)
- **Domain models** - What backend stores (complete, with IDs, timestamps)

**Benefits:**
- Clear separation of concerns
- Request models are simpler (no IDs, timestamps)
- Domain models are complete (everything needed for storage)

**Example:**
```python
# Request (SDK sends)
CreateStepRequest(name="Filter", type="filter", input={...})

# Domain (Backend stores)
Step(step_id="...", execution_id="...", name="Filter", started_at=..., ...)
```

---

## Data Flow

```
1. SDK creates request:
   CreateExecutionRequest(name="...", metadata={...})

2. Backend creates domain object:
   Execution(execution_id=uuid4(), name="...", started_at=now(), ...)

3. SDK sends evaluation:
   CreateEvaluationRequest(entity_id="...", value=..., passed=..., reason="...")

4. Backend adds to step:
   step.evaluations.append(Evaluation(...))

5. Dashboard reads:
   GET /api/executions/{id} → Returns Execution with all Steps and Evaluations
```

---

## Summary of Design Principles

1. **Hierarchical** - Execution → Step → Evaluation (clear structure)
2. **Flexible** - Dict[str, Any] for input/output (works for any domain)
3. **Entity-level** - Track individual items, not just aggregates
4. **Reason required** - Every evaluation must explain WHY
5. **Optional models** - SDK works with or without models
6. **General-purpose** - No domain-specific fields
7. **Transparent** - Rules, inputs, outputs all captured

These choices make X-Ray:
- ✅ General-purpose (works for any domain)
- ✅ Transparent (shows why decisions were made)
- ✅ Flexible (accommodates different data structures)
- ✅ Plug-and-play (SDK independent of backend)

