# X-Ray Debugging System

A powerful execution tracking and debugging system with a beautiful debugger-style UI. Track your ML pipelines, algorithms, and complex workflows step-by-step with detailed evaluations and insights.

## 🎯 Features

- **Step-by-step execution tracking** - Track every step of your algorithm
- **Evaluation recording** - Record pass/fail evaluations for each entity
- **Beautiful debugger UI** - Modern, dark-themed interface with timeline visualization
- **Real-time updates** - Live polling for active executions
- **Detailed insights** - View inputs, outputs, rules, and evaluation results
- **Python SDK** - Easy-to-use client library for instrumenting your code

## 🏗️ Architecture

```
User Application → X-Ray SDK → FastAPI Backend → React Frontend
```

- **Backend**: FastAPI with in-memory storage (easily replaceable with database)
- **Frontend**: React with Vite, modern UI components
- **SDK**: Python client library for easy integration

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
python examples/example_usage.py
```

Then open `http://localhost:3000` to see the execution in the dashboard!

## 💻 SDK Usage

### Basic Usage

```python
from sdk.xray import XRay

# Initialize client
xray = XRay("my_execution_name", api_url="http://localhost:8000")

# Start execution
xray.start_execution(metadata={"environment": "prod"})

# Start a step
xray.start_step("Filter Candidates", step_type="filter", input_data={"min_rating": 4.0})

# Record evaluations
for candidate in candidates:
    passed = candidate.rating >= 4.0
    xray.record_evaluation(
        entity_id=candidate.id,
        value=candidate.rating,
        passed=passed,
        reason=f"Rating {candidate.rating} >= 4.0" if passed else f"Rating {candidate.rating} < 4.0"
    )

# End step
xray.end_step(output={"passed": 12, "failed": 3})

# End execution
xray.end_execution(status="completed")
```

### Context Manager Usage

```python
from sdk.xray import XRay, step

xray = XRay("my_execution")
xray.start_execution()

# Use context manager for automatic step management
with step(xray, "Process Data", step_type="transform"):
    # Your code here
    xray.record_evaluation(...)
    # Step automatically ends when exiting context
```

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

## 🚧 Future Enhancements

- Database persistence (PostgreSQL, MongoDB)
- Authentication and multi-user support
- Export/import executions
- Advanced filtering and search
- Execution comparison
- Metrics and analytics
- Webhook notifications
- GraphQL API option

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

