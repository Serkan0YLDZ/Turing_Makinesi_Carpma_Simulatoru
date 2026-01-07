from typing import Callable, Optional
from ...domain.interfaces.ituring_machine import ITuringMachine
from ...domain.interfaces.itape import ITape
from ...domain.interfaces.istep_explainer import IStepExplainer
from ...domain.entities.step_result import StepResult


class MachineExecutor:
    
    def __init__(self, step_explainer: IStepExplainer):
        self._step_explainer = step_explainer
    
    def execute_with_explanation(
        self,
        machine: ITuringMachine,
        initial_tape: ITape,
        step_callback: Optional[Callable[[StepResult], None]] = None,
        max_steps: int = 100000
    ) -> StepResult:
        def enhanced_callback(result: StepResult) -> None:
            explanation = self._step_explainer.explain_step(result)
            result.explanation = explanation
            
            if step_callback:
                step_callback(result)
        
        return machine.execute(initial_tape, enhanced_callback)
    
    def step_with_explanation(self, machine: ITuringMachine) -> StepResult:
        result = machine.step()
        explanation = self._step_explainer.explain_step(result)
        result.explanation = explanation
        return result

