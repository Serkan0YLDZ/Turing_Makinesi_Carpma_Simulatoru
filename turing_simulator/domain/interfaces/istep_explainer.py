from abc import ABC, abstractmethod
from ..entities.step_result import StepResult


class IStepExplainer(ABC):
    
    @abstractmethod
    def explain_step(self, step_result: StepResult) -> str:
        pass

