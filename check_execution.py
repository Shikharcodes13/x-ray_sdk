import requests
import json

r = requests.get('http://localhost:8000/api/executions')
execs = r.json()
print(f'Found {len(execs)} execution(s)')
if execs:
    latest = execs[0]
    print(f'\nLatest execution:')
    print(f'  Name: {latest["name"]}')
    print(f'  Status: {latest["status"]}')
    print(f'  Steps: {len(latest["steps"])}')
    print(f'  Execution ID: {latest["execution_id"]}')
    for i, step in enumerate(latest["steps"], 1):
        print(f'\n  Step {i}: {step["name"]} ({step["type"]})')
        print(f'    Evaluations: {len(step.get("evaluations", []))}')

