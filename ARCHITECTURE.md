# X-Ray Architecture

## Overview

X-Ray consists of three main components:

1. **SDK** (`sdk/`) - Client library (what users import)
2. **Backend** (`backend/`) - Server implementation (API + storage)
3. **Frontend** (`frontend/`) - Dashboard UI

## Component Responsibilities

### SDK (`sdk/xray.py`)
**Purpose:** Client library that users import into their code

**Contains:**
- All tracking logic (when to send what data)
- HTTP client that makes requests to backend
- Error handling
- Context managers for easy usage

**Key Point:** This is the MAIN component - it's what gets distributed as a package.

**Example Usage:**
```python
from sdk import XRay

xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution()
xray.start_step(name="Process", step_type="transform")
xray.record_evaluation(entity_id="item_1", value=100, passed=True, reason="Valid")
xray.end_step()
xray.end_execution()
```

### Backend (`backend/`)
**Purpose:** Server that receives and stores execution data

**Contains:**
- **API Contract Definition** - The REST endpoints the SDK expects:
  - `POST /api/executions` - Create execution
  - `POST /api/executions/{id}/steps` - Create step
  - `POST /api/steps/{id}/evaluations` - Add evaluation
  - `PATCH /api/steps/{id}` - Update step
  - `PATCH /api/executions/{id}` - Update execution
  - `GET /api/executions` - List executions
  - `GET /api/executions/{id}` - Get execution details

- **Data Models** (`models.py`) - Pydantic models defining the data structure
- **Storage** (`storage.py`) - In-memory storage (can be replaced with database)
- **API Server** (`main.py`) - FastAPI server that handles HTTP requests

**Key Point:** This is a REFERENCE IMPLEMENTATION. The SDK can work with ANY backend that implements the same API contract (could be Node.js, Go, Java, etc.)

### Frontend (`frontend/`)
**Purpose:** Dashboard UI to visualize executions

**Contains:**
- React application
- Displays execution timeline
- Shows step details and evaluations
- Reads data from backend API

## Data Flow

```
User's Code
    │
    │ imports SDK
    ▼
┌─────────────┐
│  SDK (sdk/)  │  ← Main logic here
└─────────────┘
    │
    │ HTTP requests
    ▼
┌─────────────┐
│ Backend API │  ← Receives & stores data
│ (backend/)  │
└─────────────┘
    │
    │ serves data
    ▼
┌─────────────┐
│  Frontend    │  ← Displays data
│ (frontend/)  │
└─────────────┘
```

## API Contract

The backend defines the API contract that the SDK expects. Any backend system that implements these endpoints will work with the SDK:

### Required Endpoints:

1. **POST /api/executions**
   - Request: `{ "name": string, "metadata": object }`
   - Response: `{ "execution_id": string, ... }`

2. **POST /api/executions/{execution_id}/steps**
   - Request: `{ "name": string, "type": string, "input": object, "rules": array }`
   - Response: `{ "step_id": string, ... }`

3. **POST /api/steps/{step_id}/evaluations**
   - Request: `{ "entity_id": string, "value": any, "passed": bool, "reason": string }`
   - Response: Step object

4. **PATCH /api/steps/{step_id}**
   - Request: `{ "output": object, "ended_at": datetime }`
   - Response: Step object

5. **PATCH /api/executions/{execution_id}**
   - Request: `{ "status": string, "ended_at": datetime }`
   - Response: Execution object

6. **GET /api/executions**
   - Response: Array of Execution objects

7. **GET /api/executions/{execution_id}**
   - Response: Execution object with all steps

## Key Design Principles

1. **SDK is Independent**: The SDK has zero dependencies on backend implementation
2. **Backend is Replaceable**: Any system implementing the API contract works
3. **API Contract is the Interface**: The backend defines what the SDK expects
4. **Separation of Concerns**: 
   - SDK = Client logic
   - Backend = Server logic + Storage
   - Frontend = Visualization

## Can You Use a Different Backend?

**YES!** The SDK can work with:
- Node.js/Express backend
- Go backend
- Java/Spring backend
- Any language/framework that implements the API contract

You just need to implement the same REST endpoints with the same request/response formats.

