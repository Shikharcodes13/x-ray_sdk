"""
Direct API Integration Example (Without SDK)

This example shows how to integrate with X-Ray using direct HTTP API calls
instead of the SDK. Useful for:
- Non-Python languages (JavaScript, Go, Java, etc.)
- Custom HTTP clients
- Integration with existing HTTP infrastructure
"""

import requests
from datetime import datetime
from typing import List, Dict, Any

API_URL = "http://localhost:8000"


def create_execution(name: str, metadata: Dict[str, Any] = None) -> str:
    """Create a new execution and return execution_id."""
    response = requests.post(
        f"{API_URL}/api/executions",
        json={
            "name": name,
            "metadata": metadata or {}
        }
    )
    response.raise_for_status()
    execution = response.json()
    return execution["execution_id"]


def create_step(execution_id: str, name: str, step_type: str = "default",
                input_data: Dict[str, Any] = None,
                rules: List[Dict[str, Any]] = None) -> str:
    """Create a step and return step_id."""
    response = requests.post(
        f"{API_URL}/api/executions/{execution_id}/steps",
        json={
            "name": name,
            "type": step_type,
            "input": input_data or {},
            "rules": rules or []
        }
    )
    response.raise_for_status()
    step = response.json()
    return step["step_id"]


def add_evaluation(step_id: str, entity_id: str, value: Any,
                   passed: bool, reason: str):
    """Add an evaluation to a step."""
    response = requests.post(
        f"{API_URL}/api/steps/{step_id}/evaluations",
        json={
            "entity_id": entity_id,
            "value": value,
            "passed": passed,
            "reason": reason
        }
    )
    response.raise_for_status()


def update_step(step_id: str, output: Dict[str, Any] = None):
    """Update a step with output and end time."""
    response = requests.patch(
        f"{API_URL}/api/steps/{step_id}",
        json={
            "output": output or {},
            "ended_at": datetime.utcnow().isoformat() + "Z"
        }
    )
    response.raise_for_status()


def end_execution(execution_id: str, status: str = "completed"):
    """End an execution."""
    response = requests.patch(
        f"{API_URL}/api/executions/{execution_id}",
        params={
            "status": status,
            "ended_at": datetime.utcnow().isoformat() + "Z"
        }
    )
    response.raise_for_status()


def get_execution(execution_id: str) -> Dict[str, Any]:
    """Get execution details."""
    response = requests.get(f"{API_URL}/api/executions/{execution_id}")
    response.raise_for_status()
    return response.json()


def list_executions(limit: int = 100) -> List[Dict[str, Any]]:
    """List all executions."""
    response = requests.get(
        f"{API_URL}/api/executions",
        params={"limit": limit}
    )
    response.raise_for_status()
    return response.json()


# Example: Flight evaluation using direct API calls
def evaluate_flights_via_api():
    """Example flight evaluation using direct API calls."""
    
    print("=" * 60)
    print("Flight Evaluation via Direct API Integration")
    print("=" * 60)
    print()
    
    # 1. Create execution
    print("1. Creating execution...")
    execution_id = create_execution(
        name="flight_evaluation_api",
        metadata={
            "environment": "production",
            "task": "find_best_flight",
            "route": "Delhi to Mumbai",
            "budget": 40000
        }
    )
    print(f"   ✓ Created execution: {execution_id}")
    
    # Sample flight data
    flights = [
        {"id": "AI868", "from": "Delhi", "to": "Mumbai", "price": 25612},
        {"id": "AI624", "from": "Delhi", "to": "Mumbai", "price": 25612},
        {"id": "AI531", "from": "Delhi", "to": "Bangalore", "price": 42220},
    ]
    
    # 2. Step 1: Filter by Route
    print("\n2. Creating 'Filter by Route' step...")
    step1_id = create_step(
        execution_id=execution_id,
        name="Filter by Route",
        step_type="filter",
        input_data={
            "origin": "Delhi",
            "destination": "Mumbai"
        },
        rules=[{
            "rule_id": "route_match",
            "description": "Flight must be from Delhi to Mumbai",
            "operator": "==",
            "value": True,
            "source": "config"
        }]
    )
    print(f"   ✓ Created step: {step1_id}")
    
    # Add evaluations
    route_filtered = []
    for flight in flights:
        route_match = flight["from"] == "Delhi" and flight["to"] == "Mumbai"
        add_evaluation(
            step_id=step1_id,
            entity_id=flight["id"],
            value=f"{flight['from']} → {flight['to']}",
            passed=route_match,
            reason=f"Route check: {flight['from']} → {flight['to']}"
        )
        if route_match:
            route_filtered.append(flight)
    
    update_step(step1_id, output={
        "filtered_count": len(route_filtered),
        "passed": len(route_filtered),
        "failed": len(flights) - len(route_filtered)
    })
    print(f"   ✓ Filtered to {len(route_filtered)} flights")
    
    # 3. Step 2: Filter by Budget
    print("\n3. Creating 'Filter by Budget' step...")
    step2_id = create_step(
        execution_id=execution_id,
        name="Filter by Budget",
        step_type="filter",
        input_data={"max_price": 40000},
        rules=[{
            "rule_id": "budget_constraint",
            "description": "Flight price must be under Rs. 40,000",
            "operator": "<=",
            "value": 40000,
            "source": "config"
        }]
    )
    print(f"   ✓ Created step: {step2_id}")
    
    budget_filtered = []
    for flight in route_filtered:
        within_budget = flight["price"] <= 40000
        add_evaluation(
            step_id=step2_id,
            entity_id=flight["id"],
            value=flight["price"],
            passed=within_budget,
            reason=f"Price Rs. {flight['price']:,} {'<=' if within_budget else '>'} Rs. 40,000"
        )
        if within_budget:
            budget_filtered.append(flight)
    
    update_step(step2_id, output={
        "filtered_count": len(budget_filtered),
        "passed": len(budget_filtered),
        "failed": len(route_filtered) - len(budget_filtered),
        "max_price_found": max([f["price"] for f in budget_filtered]) if budget_filtered else 0
    })
    print(f"   ✓ Filtered to {len(budget_filtered)} flights under ₹40,000")
    
    # 4. Step 3: Select Best
    if budget_filtered:
        print("\n4. Creating 'Select Best Flight' step...")
        step3_id = create_step(
            execution_id=execution_id,
            name="Select Best Flight",
            step_type="select",
            input_data={"selection_criteria": "lowest price"}
        )
        print(f"   ✓ Created step: {step3_id}")
        
        # Find best (lowest price)
        best_flight = min(budget_filtered, key=lambda x: x["price"])
        
        add_evaluation(
            step_id=step3_id,
            entity_id=best_flight["id"],
            value=best_flight,
            passed=True,
            reason=f"Selected as best option - Price: Rs. {best_flight['price']:,}"
        )
        
        update_step(step3_id, output={
            "selected_flight_id": best_flight["id"],
            "selected_price": best_flight["price"],
            "rank": 1
        })
        print(f"   ✓ Selected flight: {best_flight['id']} (Rs. {best_flight['price']:,})")
    
    # 5. End execution
    print("\n5. Ending execution...")
    end_execution(execution_id, status="completed")
    print(f"   ✓ Execution completed")
    
    # 6. Retrieve and display results
    print("\n6. Retrieving execution details...")
    execution = get_execution(execution_id)
    print(f"   ✓ Execution has {len(execution['steps'])} steps")
    
    print("\n" + "=" * 60)
    print("✅ API Integration Complete!")
    print("=" * 60)
    print(f"Execution ID: {execution_id}")
    print(f"View in dashboard: http://localhost:3000")
    print(f"API endpoint: {API_URL}/api/executions/{execution_id}")
    print("=" * 60)
    
    return execution_id


if __name__ == "__main__":
    try:
        # Check if API is available
        response = requests.get(f"{API_URL}/api/health")
        response.raise_for_status()
        
        execution_id = evaluate_flights_via_api()
        print(f"\n✅ Success! Execution ID: {execution_id}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API.")
        print("   Make sure the backend is running:")
        print("   python run_backend.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

