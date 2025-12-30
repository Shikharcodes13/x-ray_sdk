from typing import Dict, Optional, List
from datetime import datetime

try:
    from .models import Execution, Step
except ImportError:
    from models import Execution, Step


class InMemoryStorage:
    """Simple in-memory storage for development. Can be replaced with database later."""
    
    def __init__(self):
        self.executions: Dict[str, Execution] = {}
        self.steps: Dict[str, Step] = {}
    
    def create_execution(self, execution: Execution) -> Execution:
        self.executions[execution.execution_id] = execution
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[Execution]:
        return self.executions.get(execution_id)
    
    def list_executions(self, limit: int = 100) -> List[Execution]:
        executions = list(self.executions.values())
        executions.sort(key=lambda x: x.started_at, reverse=True)
        return executions[:limit]
    
    def update_execution(self, execution_id: str, **kwargs) -> Optional[Execution]:
        execution = self.executions.get(execution_id)
        if execution:
            for key, value in kwargs.items():
                if hasattr(execution, key):
                    setattr(execution, key, value)
        return execution
    
    def add_step(self, execution_id: str, step: Step) -> Step:
        self.steps[step.step_id] = step
        execution = self.executions.get(execution_id)
        if execution:
            execution.steps.append(step)
        return step
    
    def get_step(self, step_id: str) -> Optional[Step]:
        return self.steps.get(step_id)
    
    def update_step(self, step_id: str, **kwargs) -> Optional[Step]:
        step = self.steps.get(step_id)
        if step:
            for key, value in kwargs.items():
                if hasattr(step, key):
                    setattr(step, key, value)
        return step


# Global storage instance
storage = InMemoryStorage()

