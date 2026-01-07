from abc import ABC, abstractmethod
from typing import Callable, Dict, Tuple
from ..entities.state import State
from ..entities.transition import Transition
from ..entities.step_result import StepResult
from .itape import ITape


class ITuringMachine(ABC):
    
    @abstractmethod
    def execute(
        self, 
        initial_tape: ITape, 
        step_callback: Callable[[StepResult], None] = None
    ) -> StepResult:
        pass
    
    @abstractmethod
    def step(self) -> StepResult:
        pass
    
    @abstractmethod
    def reset(self, tape: ITape) -> None:
        pass
    
    @abstractmethod
    def get_current_state(self) -> State:
        pass
    
    @abstractmethod
    def get_transitions(self) -> Dict[Tuple[State, str], Transition]:
        pass
    
    @abstractmethod
    def is_halted(self) -> bool:
        pass

