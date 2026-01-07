from typing import Callable, Dict, Optional, Tuple
from ..interfaces.ituring_machine import ITuringMachine
from ..interfaces.itape import ITape
from .state import State
from .transition import Transition
from .step_result import StepResult


class TuringMachine(ITuringMachine):
    
    MAX_STEPS = 100000
    
    def __init__(
        self,
        states: list[State],
        initial_state: State,
        transitions: Dict[Tuple[State, str], Transition],
        blank_symbol: str = 'B',
        final_states: Optional[list[State]] = None
    ):
        self._states = {state.name: state for state in states}
        self._initial_state = initial_state
        self._transitions = transitions
        self._blank_symbol = blank_symbol
        self._final_states = final_states or []
        
        self._current_state = initial_state
        self._tape: Optional[ITape] = None
        self._head_position = 0
        self._step_count = 0
        self._is_halted = False
    
    def execute(
        self, 
        initial_tape: ITape, 
        step_callback: Callable[[StepResult], None] = None
    ) -> StepResult:
        self.reset(initial_tape)
        last_result = None
        
        while not self.is_halted() and self._step_count < self.MAX_STEPS:
            result = self.step()
            last_result = result
            
            if step_callback:
                step_callback(result)
            
            if result.is_halted:
                break
        
        if self._step_count >= self.MAX_STEPS:
            raise RuntimeError(
                f"Makine {self.MAX_STEPS} adım içinde durmadı. "
                "Sonsuz döngü olabilir."
            )
        
        return last_result
    
    def step(self) -> StepResult:
        if self._is_halted:
            raise RuntimeError("Makine zaten durmuş durumda.")
        
        if self._tape is None:
            raise RuntimeError("Şerit başlatılmamış. reset() çağırın.")
        
        previous_state = self._current_state
        self._step_count += 1
        
        read_symbol = self._tape.read(self._head_position)
        
        transition_key = (self._current_state, read_symbol)
        transition = self._transitions.get(transition_key)
        
        if transition is None:
            self._is_halted = True
            return StepResult(
                step_number=self._step_count,
                previous_state=previous_state,
                current_state=self._current_state,
                read_symbol=read_symbol,
                write_symbol=read_symbol,
                direction='',
                head_position=self._head_position,
                tape_snapshot=self._tape.get_all_symbols(),
                is_halted=True,
                explanation=(
                    f"Geçersiz geçiş: {self._current_state.name} durumunda "
                    f"'{read_symbol}' sembolü için geçiş tanımlı değil."
                )
            )
        
        write_symbol = transition.write_symbol
        direction = transition.direction
        
        self._tape.write(self._head_position, write_symbol)
        
        if direction == 'L':
            self._head_position -= 1
        elif direction == 'R':
            self._head_position += 1
        
        self._current_state = transition.to_state
        
        if self._current_state in self._final_states:
            self._is_halted = True
        
        tape_snapshot = self._tape.get_all_symbols()
        
        return StepResult(
            step_number=self._step_count,
            previous_state=previous_state,
            current_state=self._current_state,
            read_symbol=read_symbol,
            write_symbol=write_symbol,
            direction=direction,
            head_position=self._head_position,
            tape_snapshot=tape_snapshot,
            transition=transition,
            is_halted=self._is_halted
        )
    
    def reset(self, tape: ITape) -> None:
        self._tape = tape
        self._current_state = self._initial_state
        self._head_position = 0
        self._step_count = 0
        self._is_halted = False
    
    def get_current_state(self) -> State:
        return self._current_state
    
    def get_transitions(self) -> Dict[Tuple[State, str], Transition]:
        return self._transitions.copy()
    
    def is_halted(self) -> bool:
        return self._is_halted
    
    def get_head_position(self) -> int:
        return self._head_position
    
    def get_step_count(self) -> int:
        return self._step_count

