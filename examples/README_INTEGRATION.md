# X-Ray SDK Integration Guide

The X-Ray SDK supports **three integration modes** that allow you to plug it into any system:

## 🎯 Integration Modes

### 1️⃣ Direct Code Integration

**Best for:** New code, full control, custom logic

Manually instrument your code with X-Ray tracking.

```python
from sdk import XRay, step

xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution()

with step(xray, "Filter Candidates", step_type="filter", 
          input_data={"min_rating": 4.0}) as step_ctx:
    
    # Your business logic
    candidates = get_candidates()
    filtered = [c for c in candidates if c['rating'] >= 4.0]
    
    # Record evaluations
    for candidate in candidates:
        passed = candidate['rating'] >= 4.0
        step_ctx.evaluate(
            entity_id=candidate['id'],
            value=candidate['rating'],
            condition=passed,
            reason=f"Rating {candidate['rating']} >= 4.0"
        )
    
    step_ctx.set_output({"filtered_count": len(filtered)})

xray.end_execution()
```

**Use when:**
- Writing new code
- Need fine-grained control
- Custom evaluation logic
- Complex step boundaries

---

### 2️⃣ Adapter Mode (Function Wrapping)

**Best for:** Existing code, minimal changes, quick integration

Wrap existing functions without modifying their code.

```python
from sdk import XRay, trace_function

xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution()

# Your existing function (no X-Ray code!)
def filter_candidates(candidates, min_rating):
    return [c for c in candidates if c['rating'] >= min_rating]

# Wrap it with X-Ray
@trace_function(xray, step_type="filter")
def traced_filter(candidates, min_rating):
    return filter_candidates(candidates, min_rating)

# Use the wrapped function - automatically tracked!
filtered = traced_filter(candidates, min_rating=4.0)

xray.end_execution()
```

**Use when:**
- Have existing functions
- Don't want to modify business logic
- Quick integration needed
- Functions are already well-defined

**Advanced:** Custom input/output extraction

```python
def extract_input(args, kwargs):
    return {"candidates": args[0], "min_rating": kwargs.get("min_rating", 0)}

def extract_output(result):
    return {"filtered_count": len(result), "filtered_ids": [c['id'] for c in result]}

@trace_function(xray, step_type="filter", 
                extract_input=extract_input,
                extract_output=extract_output)
def filter_candidates(candidates, min_rating):
    return [c for c in candidates if c['rating'] >= min_rating]
```

---

### 3️⃣ Data-Driven Mode (Configuration-Based)

**Best for:** Configurable pipelines, no-code workflows, external configuration

Execute steps from configuration (JSON, YAML, database, etc.).

```python
from sdk import XRay, StepRunner

xray = XRay("my_execution", api_url="http://localhost:8000")
xray.start_execution()

# Create runner
runner = StepRunner(xray)

# Register handlers for step types
def filter_handler(input_data, rules):
    candidates = input_data["candidates"]
    min_rating = input_data["min_rating"]
    
    filtered = [c for c in candidates if c['rating'] >= min_rating]
    evaluations = []
    
    for candidate in candidates:
        passed = candidate['rating'] >= min_rating
        evaluations.append({
            "entity_id": candidate['id'],
            "value": candidate['rating'],
            "passed": passed,
            "reason": f"Rating {candidate['rating']} >= {min_rating}"
        })
    
    return {
        "filtered_count": len(filtered),
        "evaluations": evaluations
    }

runner.register_handler("filter", filter_handler)

# Execute from configuration
step_config = {
    "name": "Filter Candidates",
    "type": "filter",
    "input": {
        "candidates": [...],
        "min_rating": 4.0
    },
    "rules": [
        {
            "rule_id": "min_rating",
            "description": "Minimum acceptable rating",
            "operator": ">=",
            "value": 4.0,
            "source": "config"
        }
    ]
}

output = runner.execute_step(step_config)

# Or execute a pipeline
pipeline = [step_config, another_step_config, ...]
outputs = runner.execute_pipeline(pipeline)

xray.end_execution()
```

**Use when:**
- Configurable pipelines
- External configuration (JSON/YAML files)
- No-code workflows
- Dynamic step execution
- Integration with workflow engines

---

## 🔄 Hybrid Approach

You can combine all three modes in a single execution:

```python
xray = XRay("hybrid_execution", api_url="http://localhost:8000")
xray.start_execution()

# Mode 1: Direct integration for custom logic
with step(xray, "Custom Step") as step_ctx:
    # Custom logic here
    step_ctx.set_output({"result": "custom"})

# Mode 2: Wrap existing function
@trace_function(xray, step_type="filter")
def my_filter(data):
    return filter_logic(data)

result = my_filter(data)

# Mode 3: Execute from config
runner = StepRunner(xray)
runner.register_handler("transform", transform_handler)
runner.execute_step(config_step)

xray.end_execution()
```

---

## 🎯 Choosing the Right Mode

| Scenario | Recommended Mode |
|----------|-----------------|
| New code, full control | **Direct Integration** |
| Existing functions, quick integration | **Adapter Mode** |
| Configurable pipelines | **Data-Driven** |
| Mix of above | **Hybrid** |

---

## 🚀 Quick Start Examples

See `examples/integration_modes.py` for complete working examples of all three modes.

Run it:
```bash
python examples/integration_modes.py
```

Then check the dashboard at `http://localhost:3000` to see all executions!

