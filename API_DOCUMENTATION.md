# X-Ray API Documentation

Complete REST API reference for integrating with X-Ray without using the SDK.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API has no authentication. In production, add authentication headers as needed.

## API Endpoints

### Health Check

**GET** `/api/health`

Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

---

### Executions

#### Create Execution

**POST** `/api/executions`

Create a new execution.

**Request Body:**
```json
{
  "name": "my_execution_name",
  "metadata": {
    "environment": "production",
    "trigger": "manual",
    "user": "john_doe",
    "version": "1.0.0"
  }
}
```

**Response:**
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my_execution_name",
  "status": "running",
  "started_at": "2024-01-15T10:30:00Z",
  "ended_at": null,
  "metadata": {
    "environment": "production",
    "trigger": "manual",
    "user": "john_doe",
    "version": "1.0.0"
  },
  "steps": []
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "flight_evaluation",
    "metadata": {
      "environment": "production",
      "task": "find_best_flight"
    }
  }'
```

---

#### List Executions

**GET** `/api/executions?limit=100`

List all executions (most recent first).

**Query Parameters:**
- `limit` (optional): Maximum number of executions to return (default: 100)

**Response:**
```json
[
  {
    "execution_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "flight_evaluation",
    "status": "completed",
    "started_at": "2024-01-15T10:30:00Z",
    "ended_at": "2024-01-15T10:35:00Z",
    "metadata": {...},
    "steps": [...]
  },
  ...
]
```

**cURL Example:**
```bash
curl http://localhost:8000/api/executions?limit=10
```

---

#### Get Execution

**GET** `/api/executions/{execution_id}`

Get a specific execution with all its steps and evaluations.

**Response:**
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "flight_evaluation",
  "status": "completed",
  "started_at": "2024-01-15T10:30:00Z",
  "ended_at": "2024-01-15T10:35:00Z",
  "metadata": {...},
  "steps": [
    {
      "step_id": "...",
      "name": "Filter by Route",
      "type": "filter",
      "input": {...},
      "rules": [...],
      "evaluations": [...],
      "output": {...},
      "started_at": "...",
      "ended_at": "..."
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/executions/550e8400-e29b-41d4-a716-446655440000
```

---

#### Update Execution

**PATCH** `/api/executions/{execution_id}?status=completed&ended_at=2024-01-15T10:35:00Z`

Update execution status and end time.

**Query Parameters:**
- `status` (optional): New status ("running", "completed", "failed")
- `ended_at` (optional): End timestamp (ISO 8601 format)

**Response:**
```json
{
  "execution_id": "...",
  "status": "completed",
  "ended_at": "2024-01-15T10:35:00Z",
  ...
}
```

**cURL Example:**
```bash
curl -X PATCH "http://localhost:8000/api/executions/550e8400-e29b-41d4-a716-446655440000?status=completed&ended_at=2024-01-15T10:35:00Z"
```

---

### Steps

#### Create Step

**POST** `/api/executions/{execution_id}/steps`

Create a new step within an execution.

**Request Body:**
```json
{
  "name": "Filter by Route",
  "type": "filter",
  "input": {
    "origin": "Delhi",
    "destination": "Mumbai"
  },
  "rules": [
    {
      "rule_id": "route_match",
      "description": "Flight must be from Delhi to Mumbai",
      "operator": "==",
      "value": true,
      "source": "config"
    }
  ]
}
```

**Response:**
```json
{
  "step_id": "660e8400-e29b-41d4-a716-446655440001",
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Filter by Route",
  "type": "filter",
  "input": {...},
  "rules": [...],
  "evaluations": [],
  "output": {},
  "started_at": "2024-01-15T10:30:05Z",
  "ended_at": null
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/executions/550e8400-e29b-41d4-a716-446655440000/steps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Filter by Route",
    "type": "filter",
    "input": {
      "origin": "Delhi",
      "destination": "Mumbai"
    },
    "rules": []
  }'
```

---

#### List Steps

**GET** `/api/executions/{execution_id}/steps`

List all steps for an execution.

**Response:**
```json
[
  {
    "step_id": "...",
    "name": "Filter by Route",
    "type": "filter",
    ...
  },
  ...
]
```

**cURL Example:**
```bash
curl http://localhost:8000/api/executions/550e8400-e29b-41d4-a716-446655440000/steps
```

---

#### Get Step

**GET** `/api/steps/{step_id}`

Get a specific step with all its evaluations.

**Response:**
```json
{
  "step_id": "660e8400-e29b-41d4-a716-446655440001",
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Filter by Route",
  "type": "filter",
  "input": {...},
  "rules": [...],
  "evaluations": [
    {
      "entity_id": "AI868",
      "value": "Delhi → Mumbai",
      "passed": true,
      "reason": "Route check: Delhi → Mumbai"
    }
  ],
  "output": {
    "filtered_count": 150,
    "passed": 150,
    "failed": 50
  },
  "started_at": "2024-01-15T10:30:05Z",
  "ended_at": "2024-01-15T10:30:10Z"
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/steps/660e8400-e29b-41d4-a716-446655440001
```

---

#### Update Step

**PATCH** `/api/steps/{step_id}`

Update a step (typically to add output and end time).

**Request Body:**
```json
{
  "output": {
    "filtered_count": 150,
    "passed": 150,
    "failed": 50,
    "data": {
      "sample_ids": ["AI868", "AI624"]
    }
  },
  "ended_at": "2024-01-15T10:30:10Z"
}
```

**Response:**
```json
{
  "step_id": "...",
  "output": {...},
  "ended_at": "2024-01-15T10:30:10Z",
  ...
}
```

**cURL Example:**
```bash
curl -X PATCH http://localhost:8000/api/steps/660e8400-e29b-41d4-a716-446655440001 \
  -H "Content-Type: application/json" \
  -d '{
    "output": {
      "filtered_count": 150,
      "passed": 150,
      "failed": 50
    }
  }'
```

---

### Evaluations

#### Add Evaluation

**POST** `/api/steps/{step_id}/evaluations`

Add an evaluation to a step.

**Request Body:**
```json
{
  "entity_id": "AI868",
  "value": "Delhi → Mumbai",
  "passed": true,
  "reason": "Route check: Delhi → Mumbai"
}
```

**Response:**
```json
{
  "step_id": "...",
  "evaluations": [
    {
      "entity_id": "AI868",
      "value": "Delhi → Mumbai",
      "passed": true,
      "reason": "Route check: Delhi → Mumbai"
    }
  ],
  ...
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/steps/660e8400-e29b-41d4-a716-446655440001/evaluations \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "AI868",
    "value": "Delhi → Mumbai",
    "passed": true,
    "reason": "Route check: Delhi → Mumbai"
  }'
```

---

## Complete Integration Example (Without SDK)

Here's a complete example of integrating without the SDK using direct HTTP calls:

```python
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

# 1. Create execution
response = requests.post(
    f"{API_URL}/api/executions",
    json={
        "name": "flight_evaluation",
        "metadata": {
            "environment": "production",
            "task": "find_best_flight"
        }
    }
)
execution = response.json()
execution_id = execution["execution_id"]

# 2. Create step
response = requests.post(
    f"{API_URL}/api/executions/{execution_id}/steps",
    json={
        "name": "Filter by Route",
        "type": "filter",
        "input": {
            "origin": "Delhi",
            "destination": "Mumbai"
        },
        "rules": [
            {
                "rule_id": "route_match",
                "description": "Flight must be from Delhi to Mumbai",
                "operator": "==",
                "value": True,
                "source": "config"
            }
        ]
    }
)
step = response.json()
step_id = step["step_id"]

# 3. Add evaluations
flights = [
    {"id": "AI868", "from": "Delhi", "to": "Mumbai"},
    {"id": "AI624", "from": "Delhi", "to": "Mumbai"},
    {"id": "AI531", "from": "Delhi", "to": "Bangalore"},
]

for flight in flights:
    route_match = flight["from"] == "Delhi" and flight["to"] == "Mumbai"
    
    requests.post(
        f"{API_URL}/api/steps/{step_id}/evaluations",
        json={
            "entity_id": flight["id"],
            "value": f"{flight['from']} → {flight['to']}",
            "passed": route_match,
            "reason": f"Route check: {flight['from']} → {flight['to']}"
        }
    )

# 4. Update step with output
requests.patch(
    f"{API_URL}/api/steps/{step_id}",
    json={
        "output": {
            "filtered_count": 2,
            "passed": 2,
            "failed": 1
        }
    }
)

# 5. End execution
requests.patch(
    f"{API_URL}/api/executions/{execution_id}",
    params={
        "status": "completed",
        "ended_at": datetime.utcnow().isoformat() + "Z"
    }
)
```

---

## JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000';

async function createExecution() {
  const response = await axios.post(`${API_URL}/api/executions`, {
    name: 'flight_evaluation',
    metadata: {
      environment: 'production',
      task: 'find_best_flight'
    }
  });
  
  return response.data.execution_id;
}

async function createStep(executionId) {
  const response = await axios.post(
    `${API_URL}/api/executions/${executionId}/steps`,
    {
      name: 'Filter by Route',
      type: 'filter',
      input: {
        origin: 'Delhi',
        destination: 'Mumbai'
      },
      rules: []
    }
  );
  
  return response.data.step_id;
}

async function addEvaluation(stepId, entityId, value, passed, reason) {
  await axios.post(
    `${API_URL}/api/steps/${stepId}/evaluations`,
    {
      entity_id: entityId,
      value: value,
      passed: passed,
      reason: reason
    }
  );
}

// Usage
(async () => {
  const executionId = await createExecution();
  const stepId = await createStep(executionId);
  
  await addEvaluation(stepId, 'AI868', 'Delhi → Mumbai', true, 'Route match');
  
  await axios.patch(`${API_URL}/api/steps/${stepId}`, {
    output: { filtered_count: 1 }
  });
  
  await axios.patch(`${API_URL}/api/executions/${executionId}`, null, {
    params: { status: 'completed' }
  });
})();
```

---

## OpenAPI/Swagger Documentation

FastAPI automatically generates OpenAPI documentation. Access it at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Rate Limiting

Currently, there is no rate limiting. In production, implement rate limiting as needed.

---

## Webhooks (Future)

Webhook support for execution completion events is planned for future releases.

