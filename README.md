.# X-Ray Debugging System

A powerful execution tracking and debugging system for multi-step, non-deterministic algorithmic systems. Unlike traditional tracing that shows *what* happened, X-Ray shows *why* decisions were made at each step, making it easy to debug complex pipelines.

**Perfect for:** LLM workflows, search and ranking systems, filtering pipelines, recommendation engines, and any multi-step decision process.

## 🎯 Features

- **Step-by-step execution tracking** - Track every step of your algorithm with full context
- **Decision reasoning capture** - Record *why* each decision was made, not just what happened
- **Entity-level evaluations** - Track pass/fail for each candidate with detailed reasoning
- **Beautiful debugger UI** - Modern, dark-themed interface with timeline visualization
- **Real-time updates** - Live polling for active executions
- **Multiple integration modes** - Direct code integration, adapter mode, or data-driven configuration
- **General-purpose SDK** - Works with any domain, not tied to specific use cases

## 🏗️ Architecture

```
User Application → X-Ray SDK → FastAPI Backend → React Frontend
```

- **SDK**: Python client library - lightweight, plug-and-play, works with any backend implementing the API contract
- **Backend**: FastAPI with in-memory storage (easily replaceable with database)
- **Frontend**: React with Vite, modern UI components for visualizing execution trails

### Design Philosophy

X-Ray is designed to answer the question: **"Why did the system make this decision?"** rather than just "What happened?"

- **Captures reasoning**: Every evaluation includes a `reason` field explaining why it passed or failed
- **Entity-level tracking**: Track individual candidates/items through the pipeline, not just aggregate metrics
- **Context preservation**: Inputs, outputs, and rules are preserved for each step
- **General-purpose**: Not tied to any specific domain - works for competitor selection, content recommendation, lead scoring, etc.

## 📦 Installation

### Prerequisites

- Python 3.8+
- Node.js 16+

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## 🚀 Running the System

### 1. Start the Backend

```bash
# Option 1: Using the run script
python run_backend.py

# Option 2: Using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:3000`

### 3. Run Example Code

In a new terminal:

```bash
# Basic example
python examples/example_usage.py

# Flight evaluation (filter → rank → select)
python examples/flight_evaluation.py

# All 3 integration modes demonstration
python examples/all_modes_example.py

# Quote filtering example
python examples/life_shortest_quote.py
```

Then open `http://localhost:3000` to see the execution in the dashboard!

## 📚 Example Applications

The `examples/` directory contains several demo applications showcasing X-Ray:

- **`example_usage.py`** - Basic candidate ranking example
- **`flight_evaluation.py`** - Flight selection pipeline (filter by route → filter by budget → rank → select)
- **`all_modes_example.py`** - Demonstrates all 3 integration modes in one execution
- **`life_shortest_quote.py`** - Quote filtering example (filter by theme → find shortest)
- **`integration_modes.py`** - Detailed examples of each integration mode
- **`api_integration_example.py`** - Direct API integration without SDK

## 💻 SDK Usage

### Basic Usage

```python
from sdk import XRay, step

# Initialize client
xray = XRay("my_execution_name", api_url="http://localhost:8000")
xray.start_execution(metadata={"environment": "prod"})

# Use context manager for automatic step management
with step(xray, "Filter Candidates", step_type="filter", 
          input_data={"min_rating": 4.0}) as step_ctx:
    
    # Your business logic
    for candidate in candidates:
        passed = candidate.rating >= 4.0
        
        # Record evaluation with reasoning
        step_ctx.evaluate(
            entity_id=candidate.id,
            value=candidate.rating,
            condition=passed,
            reason=f"Rating {candidate.rating} >= 4.0" if passed 
                  else f"Rating {candidate.rating} < 4.0 threshold"
        )
    
    step_ctx.set_output({"passed": 12, "failed": 3})

xray.end_execution(status="completed")
```

### Key Point: Capture the "Why"

The `reason` parameter is crucial - it explains **why** each decision was made:

```python
step_ctx.evaluate(
    entity_id="product_123",
    value=8.99,
    condition=False,
    reason="Price $8.99 is below minimum $12.50 (0.5x of reference price $25.00)"
)
```

This level of detail makes debugging straightforward - you can immediately see why products were included or excluded.

### Integration Modes

X-Ray supports three integration modes:

1. **Direct Code Integration** - Manual instrumentation (shown above)
2. **Adapter Mode** - Wrap existing functions with decorators
3. **Data-Driven Mode** - Execute steps from configuration

See `examples/integration_modes.py` and `examples/README_INTEGRATION.md` for details.

## 📡 API Endpoints

### Executions

- `POST /api/executions` - Create a new execution
- `GET /api/executions` - List all executions
- `GET /api/executions/{id}` - Get execution details
- `PATCH /api/executions/{id}` - Update execution status

### Steps

- `POST /api/executions/{id}/steps` - Create a step
- `GET /api/executions/{id}/steps` - List steps for an execution
- `GET /api/steps/{id}` - Get step details
- `PATCH /api/steps/{id}` - Update step (add output, end time)

### Evaluations

- `POST /api/steps/{id}/evaluations` - Add an evaluation to a step

## 🎨 UI Features

### Execution List
- View all executions with status indicators
- See step counts and durations
- Quick navigation to execution details

### Execution View
- **Timeline**: Visual step timeline with status indicators
- **Step Viewer**: Detailed view of selected step
  - Evaluations table with pass/fail status
  - Input/Output JSON viewers
  - Rules display
  - Filter to show only failed evaluations

### Design
- Dark theme optimized for long debugging sessions
- Smooth animations and transitions
- Responsive design for all screen sizes
- Real-time updates via polling

## 🔧 Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic data models
│   └── storage.py       # In-memory storage (replaceable)
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── sdk/
│   ├── __init__.py
│   └── xray.py          # Python SDK client
├── examples/
│   └── example_usage.py # Example code
├── requirements.txt
├── run_backend.py
└── README.md
```

## 🔄 Data Models

### Execution
- `execution_id`: Unique identifier
- `name`: Execution name
- `status`: running, completed, failed
- `started_at`, `ended_at`: Timestamps
- `metadata`: Custom metadata
- `steps`: List of steps

### Step
- `step_id`: Unique identifier
- `name`: Step name
- `type`: Step type (filter, rank, transform, etc.)
- `input`: Input data
- `rules`: Rule definitions
- `evaluations`: List of evaluations
- `output`: Output data
- `started_at`, `ended_at`: Timestamps

### Evaluation
- `entity_id`: Entity being evaluated
- `value`: Evaluation value
- `passed`: Boolean result
- `reason`: Human-readable reason

## 💡 Approach & Design Decisions

### Why This Architecture?

1. **SDK-First Design**: The SDK is the main component - it's lightweight, has no backend dependencies, and works with any system implementing the API contract. This makes it truly plug-and-play.

2. **Reasoning as First-Class Citizen**: Every evaluation includes a `reason` field. This is the core differentiator from traditional tracing - we capture *why* decisions were made, not just what happened.

3. **Entity-Level Tracking**: We track individual entities (candidates, products, etc.) through the pipeline, not just aggregate metrics. This lets you see exactly why each item passed or failed.

4. **General-Purpose**: The SDK doesn't know about "products" or "candidates" - it just tracks executions, steps, and evaluations. This makes it reusable across any domain.

5. **Optional Validation**: Models are optional helpers for type safety. The SDK works with plain dictionaries, making it compatible with any backend that implements the API contract.

6. **Multiple Integration Modes**: Three ways to integrate (direct, adapter, data-driven) accommodate different codebases and workflows.

### Trade-offs Made

- **In-memory storage**: Chosen for simplicity and to focus on the core X-Ray concept. Easy to replace with a database.
- **HTTP-based**: Simple, language-agnostic, works over networks. Could be optimized with gRPC or WebSockets for high-throughput scenarios.

- **Python SDK only**: Focused on one language for the demo. The API contract allows SDKs in any language.

## ⚠️ Known Limitations

1. **No persistence**: Data is stored in-memory and lost on server restart. For production, replace `backend/storage.py` with database persistence.

2. **No authentication**: The API has no authentication. Add authentication middleware for production use.

3. **Single-user**: The dashboard shows all executions. Multi-user support would require user isolation.

4. **No data retention**: All executions are kept indefinitely. Consider adding TTL or archival for long-running systems.

5. **Limited querying**: Can't search or filter executions by metadata. Would need additional endpoints.

6. **No execution comparison**: Can't compare two executions side-by-side. Useful for debugging regressions.

7. **Polling-based updates**: Dashboard polls for updates rather than using WebSockets. Less efficient for high-frequency updates.

8. **Python SDK only**: Only Python SDK provided. Other languages would need their own SDK implementations (but can use the REST API directly).

## 🚧 Future Enhancements

- Database persistence (PostgreSQL, MongoDB)
- Authentication and multi-user support
- Export/import executions
- Advanced filtering and search
- Execution comparison
- Metrics and analytics
- Webhook notifications
- GraphQL API option
- WebSocket support for real-time updates
- SDK implementations for other languages (Node.js, Go, etc.)

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

