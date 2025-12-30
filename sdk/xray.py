"""
X-Ray SDK for Python
Enables developers to instrument their code with execution tracking.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4


class XRay:
    """Main X-Ray client for tracking executions, steps, and evaluations."""
    
    def __init__(self, execution_name: str, api_url: str = "http://localhost:8000"):
        """
        Initialize X-Ray client.
        
        Args:
            execution_name: Name for this execution
            api_url: Base URL of the X-Ray API server
        """
        self.execution_name = execution_name
        self.api_url = api_url.rstrip('/')
        self.execution_id: Optional[str] = None
        self.current_step_id: Optional[str] = None
    
    def start_execution(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new execution.
        
        Args:
            metadata: Optional metadata dictionary
            
        Returns:
            execution_id
        """
        response = requests.post(
            f"{self.api_url}/api/executions",
            json={
                "name": self.execution_name,
                "metadata": metadata or {}
            }
        )
        response.raise_for_status()
        data = response.json()
        self.execution_id = data["execution_id"]
        return self.execution_id
    
    def start_step(
        self,
        name: str,
        step_type: str = "default",
        input_data: Optional[Dict[str, Any]] = None,
        rules: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Start a new step within the current execution.
        
        Args:
            name: Step name
            step_type: Type of step (e.g., "filter", "rank", "transform")
            input_data: Input data for this step
            rules: List of rule definitions
            
        Returns:
            step_id
        """
        if not self.execution_id:
            raise ValueError("Must call start_execution() first")
        
        response = requests.post(
            f"{self.api_url}/api/executions/{self.execution_id}/steps",
            json={
                "name": name,
                "type": step_type,
                "input": input_data or {},
                "rules": rules or []
            }
        )
        response.raise_for_status()
        data = response.json()
        self.current_step_id = data["step_id"]
        return self.current_step_id
    
    def record_evaluation(
        self,
        entity_id: str,
        value: Any,
        passed: bool,
        reason: str
    ):
        """
        Record an evaluation result for an entity.
        
        Args:
            entity_id: Unique identifier for the entity being evaluated
            value: The value being evaluated
            passed: Whether the evaluation passed
            reason: Human-readable reason for the result
        """
        if not self.current_step_id:
            raise ValueError("Must call start_step() first")
        
        response = requests.post(
            f"{self.api_url}/api/steps/{self.current_step_id}/evaluations",
            json={
                "entity_id": entity_id,
                "value": value,
                "passed": passed,
                "reason": reason
            }
        )
        response.raise_for_status()
    
    def end_step(self, output: Optional[Dict[str, Any]] = None):
        """
        End the current step.
        
        Args:
            output: Output data for this step
        """
        if not self.current_step_id:
            raise ValueError("No active step to end")
        
        response = requests.patch(
            f"{self.api_url}/api/steps/{self.current_step_id}",
            json={
                "output": output or {}
            }
        )
        response.raise_for_status()
        self.current_step_id = None
    
    def end_execution(self, status: str = "completed"):
        """
        End the current execution.
        
        Args:
            status: Final status ("completed", "failed", etc.)
        """
        if not self.execution_id:
            raise ValueError("No active execution to end")
        
        response = requests.patch(
            f"{self.api_url}/api/executions/{self.execution_id}",
            params={
                "status": status,
                "ended_at": datetime.utcnow().isoformat() + "Z"
            }
        )
        response.raise_for_status()
        self.execution_id = None


# Context manager support for easier usage
class XRayStep:
    """Context manager for steps."""
    
    def __init__(self, xray: XRay, name: str, step_type: str = "default", 
                 input_data: Optional[Dict[str, Any]] = None,
                 rules: Optional[List[Dict[str, Any]]] = None):
        self.xray = xray
        self.name = name
        self.step_type = step_type
        self.input_data = input_data
        self.rules = rules
    
    def __enter__(self):
        self.xray.start_step(self.name, self.step_type, self.input_data, self.rules)
        return self.xray
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        output = {}
        if exc_type:
            output["error"] = str(exc_val)
        self.xray.end_step(output)
        return False


# Convenience function for context manager usage
def step(xray: XRay, name: str, step_type: str = "default",
         input_data: Optional[Dict[str, Any]] = None,
         rules: Optional[List[Dict[str, Any]]] = None):
    """Create a context manager for a step."""
    return XRayStep(xray, name, step_type, input_data, rules)

