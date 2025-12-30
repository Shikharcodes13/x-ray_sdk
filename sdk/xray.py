"""
X-Ray SDK for Python
Enables developers to instrument their code with execution tracking.

This SDK is a standalone client library that can be used with any backend system
that implements the X-Ray API contract. It makes HTTP requests to track executions,
steps, and evaluations without any backend-specific dependencies.
"""

import requests
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from uuid import uuid4


class XRayError(Exception):
    """Base exception for X-Ray SDK errors."""
    pass


class XRay:
    """
    Main X-Ray client for tracking executions, steps, and evaluations.
    
    This is a pure client library that communicates with any X-Ray-compatible
    backend via HTTP REST API. It has no dependencies on backend implementation
    details and can be used with any system that implements the API contract.
    
    Example:
        >>> xray = XRay("my_execution", api_url="https://api.example.com")
        >>> xray.start_execution(metadata={"environment": "prod"})
        >>> xray.start_step(name="Process Data", step_type="transform")
        >>> xray.record_evaluation(entity_id="item_1", value=100, passed=True, reason="Valid")
        >>> xray.end_step(output={"processed": 1})
        >>> xray.end_execution(status="completed")
    """
    
    def __init__(self, execution_name: str, api_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize X-Ray client.
        
        Args:
            execution_name: Name for this execution
            api_url: Base URL of the X-Ray API server (can be any backend)
            timeout: Request timeout in seconds (default: 30)
        """
        self.execution_name = execution_name
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.execution_id: Optional[str] = None
        self.current_step_id: Optional[str] = None
    
    def start_execution(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new execution.
        
        Args:
            metadata: Optional metadata dictionary
            
        Returns:
            execution_id
            
        Raises:
            XRayError: If the API request fails
        """
        try:

            response = requests.post(
                f"{self.api_url}/api/executions",
                json={
                    "name": self.execution_name,
                    "metadata": metadata or {}
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self.execution_id = data["execution_id"]
            return self.execution_id
        except requests.RequestException as e:
            raise XRayError(f"Failed to start execution: {str(e)}") from e
    
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
            
        Raises:
            ValueError: If no execution has been started
            XRayError: If the API request fails
        """
        if not self.execution_id:
            raise ValueError("Must call start_execution() first")
        
        try:
            response = requests.post(
                f"{self.api_url}/api/executions/{self.execution_id}/steps",
                json={
                    "name": name,
                    "type": step_type,
                    "input": input_data or {},
                    "rules": rules or []
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self.current_step_id = data["step_id"]
            return self.current_step_id
        except requests.RequestException as e:
            raise XRayError(f"Failed to start step: {str(e)}") from e
    
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
            
        Raises:
            ValueError: If no step has been started
            XRayError: If the API request fails
        """
        if not self.current_step_id:
            raise ValueError("Must call start_step() first")
        
        try:
            response = requests.post(
                f"{self.api_url}/api/steps/{self.current_step_id}/evaluations",
                json={
                    "entity_id": entity_id,
                    "value": value,
                    "passed": passed,
                    "reason": reason
                },
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise XRayError(f"Failed to record evaluation: {str(e)}") from e
    
    def end_step(self, output: Optional[Dict[str, Any]] = None):
        """
        End the current step.
        
        Args:
            output: Output data for this step
            
        Raises:
            ValueError: If no step is active
            XRayError: If the API request fails
        """
        if not self.current_step_id:
            raise ValueError("No active step to end")
        
        try:
            response = requests.patch(
                f"{self.api_url}/api/steps/{self.current_step_id}",
                json={
                    "output": output or {}
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            self.current_step_id = None
        except requests.RequestException as e:
            raise XRayError(f"Failed to end step: {str(e)}") from e
    
    def end_execution(self, status: str = "completed"):
        """
        End the current execution.
        
        Args:
            status: Final status ("completed", "failed", etc.)
            
        Raises:
            ValueError: If no execution is active
            XRayError: If the API request fails
        """
        if not self.execution_id:
            raise ValueError("No active execution to end")
        
        try:
            response = requests.patch(
                f"{self.api_url}/api/executions/{self.execution_id}",
                params={
                    "status": status,
                    "ended_at": datetime.utcnow().isoformat() + "Z"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            self.execution_id = None
        except requests.RequestException as e:
            raise XRayError(f"Failed to end execution: {str(e)}") from e


# Enhanced Step Context Manager with helper methods
class StepContext:
    """
    Enhanced context manager for steps that provides helper methods.
    
    This allows you to easily record evaluations and set output within a step context.
    """
    
    def __init__(self, xray: XRay, name: str, step_type: str = "default", 
                 input_data: Optional[Dict[str, Any]] = None,
                 rules: Optional[List[Dict[str, Any]]] = None):
        self.xray = xray
        self.name = name
        self.step_type = step_type
        self.input_data = input_data
        self.rules = rules
        self._output: Optional[Dict[str, Any]] = None
        self._error: Optional[str] = None
    
    def __enter__(self):
        self.xray.start_step(self.name, self.step_type, self.input_data, self.rules)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        output = self._output or {}
        if exc_type:
            output["error"] = str(exc_val)
            self._error = str(exc_val)
        self.xray.end_step(output)
        return False
    
    def log_evaluation(self, entity_id: str, value: Any, passed: bool, reason: str):
        """
        Record an evaluation within this step.
        
        Args:
            entity_id: Unique identifier for the entity
            value: The value being evaluated
            passed: Whether the evaluation passed
            reason: Human-readable reason
        """
        self.xray.record_evaluation(entity_id, value, passed, reason)
    
    def set_output(self, output: Dict[str, Any]):
        """
        Set the output for this step.
        
        Args:
            output: Output data dictionary
        """
        self._output = output
    
    def evaluate(self, entity_id: str, value: Any, condition: bool, reason: str = None):
        """
        Convenience method to evaluate an entity with automatic pass/fail.
        
        Args:
            entity_id: Unique identifier for the entity
            value: The value being evaluated
            condition: Boolean condition (True = passed, False = failed)
            reason: Optional reason (auto-generated if not provided)
        """
        if reason is None:
            reason = f"Evaluation {'passed' if condition else 'failed'}"
        self.log_evaluation(entity_id, value, condition, reason)
        return condition


# Convenience function for context manager usage
def step(xray: XRay, name: str, step_type: str = "default",
         input_data: Optional[Dict[str, Any]] = None,
         rules: Optional[List[Dict[str, Any]]] = None):
    """
    Create a context manager for a step.
    
    Example:
        >>> with xray.step("Filter Candidates", input_data={"min_rating": 4.0}) as step:
        ...     step.log_evaluation("item_1", 4.5, True, "Rating >= 4.0")
        ...     step.set_output({"filtered": 3})
    """
    return StepContext(xray, name, step_type, input_data, rules)


# Decorator support for wrapping functions
def trace_function(xray: XRay, step_type: str = "default", 
                   extract_input: Optional[Callable] = None,
                   extract_output: Optional[Callable] = None,
                   extract_evaluations: Optional[Callable] = None):
    """
    Decorator to automatically trace function execution.
    
    This allows you to wrap existing functions without modifying their code.
    
    Args:
        xray: XRay instance
        step_type: Type of step (default: "default")
        extract_input: Function to extract input data from function args/kwargs
        extract_output: Function to extract output data from return value
        extract_evaluations: Function to extract evaluations from return value
    
    Example:
        >>> @trace_function(xray, step_type="filter")
        >>> def filter_candidates(candidates, min_rating):
        ...     return [c for c in candidates if c['rating'] >= min_rating]
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract input if function provided
            input_data = {}
            if extract_input:
                input_data = extract_input(args, kwargs)
            else:
                # Default: capture args and kwargs
                if args:
                    input_data["args"] = args
                if kwargs:
                    input_data.update(kwargs)
            
            # Start step
            with StepContext(xray, name=func.__name__, step_type=step_type, input_data=input_data) as step_ctx:
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Extract output if function provided
                    output = {}
                    if extract_output:
                        output = extract_output(result)
                    else:
                        output = {"result": result}
                    
                    # Extract evaluations if function provided
                    if extract_evaluations:
                        evals = extract_evaluations(result)
                        for eval_data in evals:
                            step_ctx.log_evaluation(**eval_data)
                    
                    step_ctx.set_output(output)
                    return result
                except Exception as e:
                    step_ctx.set_output({"error": str(e)})
                    raise
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


# Generic step runner for data-driven execution
class StepRunner:
    """
    Generic step runner that can execute steps from configuration.
    
    This enables data-driven execution where steps are defined in config files
    rather than code.
    """
    
    def __init__(self, xray: XRay):
        self.xray = xray
        self._step_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, step_type: str, handler: Callable):
        """
        Register a handler function for a specific step type.
        
        Args:
            step_type: Type of step (e.g., "filter", "transform", "rank")
            handler: Function that takes (input_data, rules) and returns output
        
        Example:
            >>> runner = StepRunner(xray)
            >>> runner.register_handler("filter", lambda input, rules: filter_data(input, rules))
        """
        self._step_handlers[step_type] = handler
    
    def execute_step(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a step from configuration.
        
        Args:
            step_config: Step configuration dict with:
                - name: Step name
                - type: Step type (must have registered handler)
                - input: Input data
                - rules: Optional rules
        
        Returns:
            Step output
        
        Example:
            >>> config = {
            ...     "name": "Filter Candidates",
            ...     "type": "filter",
            ...     "input": {"candidates": [...], "min_rating": 4.0},
            ...     "rules": [{"field": "rating", "op": ">=", "value": 4.0}]
            ... }
            >>> output = runner.execute_step(config)
        """
        step_name = step_config.get("name", "Unnamed Step")
        step_type = step_config.get("type", "default")
        input_data = step_config.get("input", {})
        rules = step_config.get("rules", [])
        
        if step_type not in self._step_handlers:
            raise ValueError(f"No handler registered for step type: {step_type}")
        
        handler = self._step_handlers[step_type]
        
        with step(self.xray, step_name, step_type, input_data, rules) as step_ctx:
            try:
                # Execute handler
                result = handler(input_data, rules)
                
                # If result is a dict with evaluations, extract them
                if isinstance(result, dict) and "evaluations" in result:
                    evals = result.pop("evaluations")
                    for eval_data in evals:
                        step_ctx.log_evaluation(**eval_data)
                
                # Set output
                output = result if isinstance(result, dict) else {"result": result}
                step_ctx.set_output(output)
                
                return output
            except Exception as e:
                step_ctx.set_output({"error": str(e)})
                raise
    
    def execute_pipeline(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a pipeline of steps from configuration.
        
        Args:
            steps: List of step configurations
        
        Returns:
            List of step outputs
        
        Example:
            >>> pipeline = [
            ...     {"name": "Step 1", "type": "transform", "input": {...}},
            ...     {"name": "Step 2", "type": "filter", "input": {...}},
            ... ]
            >>> outputs = runner.execute_pipeline(pipeline)
        """
        outputs = []
        for step_config in steps:
            output = self.execute_step(step_config)
            outputs.append(output)
        return outputs

