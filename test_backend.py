"""
Simple test script to verify the backend is working.
Run this after starting the backend server.
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_backend():
    print("Testing X-Ray Backend API...")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/health")
        print(f"   ✓ Health check: {response.json()}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        return False
    
    # Test create execution
    print("\n2. Testing create execution...")
    try:
        response = requests.post(
            f"{API_URL}/api/executions",
            json={"name": "test_execution", "metadata": {}}
        )
        execution = response.json()
        execution_id = execution["execution_id"]
        print(f"   ✓ Created execution: {execution_id}")
    except Exception as e:
        print(f"   ✗ Create execution failed: {e}")
        return False
    
    # Test create step
    print("\n3. Testing create step...")
    try:
        response = requests.post(
            f"{API_URL}/api/executions/{execution_id}/steps",
            json={
                "name": "test_step",
                "type": "test",
                "input": {"test": "data"}
            }
        )
        step = response.json()
        step_id = step["step_id"]
        print(f"   ✓ Created step: {step_id}")
    except Exception as e:
        print(f"   ✗ Create step failed: {e}")
        return False
    
    # Test add evaluation
    print("\n4. Testing add evaluation...")
    try:
        response = requests.post(
            f"{API_URL}/api/steps/{step_id}/evaluations",
            json={
                "entity_id": "entity_1",
                "value": 4.5,
                "passed": True,
                "reason": "Test evaluation"
            }
        )
        print(f"   ✓ Added evaluation")
    except Exception as e:
        print(f"   ✗ Add evaluation failed: {e}")
        return False
    
    # Test get execution
    print("\n5. Testing get execution...")
    try:
        response = requests.get(f"{API_URL}/api/executions/{execution_id}")
        execution = response.json()
        print(f"   ✓ Retrieved execution with {len(execution.get('steps', []))} step(s)")
    except Exception as e:
        print(f"   ✗ Get execution failed: {e}")
        return False
    
    # Test list executions
    print("\n6. Testing list executions...")
    try:
        response = requests.get(f"{API_URL}/api/executions")
        executions = response.json()
        print(f"   ✓ Found {len(executions)} execution(s)")
    except Exception as e:
        print(f"   ✗ List executions failed: {e}")
        return False
    
    print("\n✅ All tests passed! Backend is working correctly.")
    return True

if __name__ == "__main__":
    success = test_backend()
    exit(0 if success else 1)

