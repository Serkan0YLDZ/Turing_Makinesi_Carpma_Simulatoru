from dataclasses import dataclass
from typing import Dict, Optional
from .state import State
from .transition import Transition


@dataclass
class StepResult:
    step_number: int
    previous_state: State
    current_state: State
    read_symbol: str
    write_symbol: str
    direction: str
    head_position: int
    tape_snapshot: Dict[int, str]
    transition: Optional[Transition] = None
    is_halted: bool = False
    explanation: str = ""
    
    def __str__(self) -> str:
        return (f"Adım {self.step_number}: {self.previous_state.name} → "
                f"{self.current_state.name} | Okunan: {self.read_symbol}, "
                f"Yazılan: {self.write_symbol}, Yön: {self.direction}")
    
    def get_tape_visualization(self, context_size: int = 5) -> str:
        if not self.tape_snapshot:
            return "(Boş şerit)"
        
        min_pos = min(self.tape_snapshot.keys())
        max_pos = max(self.tape_snapshot.keys())
        
        display_min = max(min_pos, self.head_position - context_size)
        display_max = min(max_pos, self.head_position + context_size)
        
        symbols = []
        positions = []
        for pos in range(display_min, display_max + 1):
            symbol = self.tape_snapshot.get(pos, 'B')
            symbols.append(symbol if symbol != 'B' else '□')
            positions.append(pos)
        
        tape_str = " ".join(symbols)
        head_marker_pos = self.head_position - display_min
        
        marker_line = " " * (head_marker_pos * 2) + "↑"
        
        return (f"{tape_str}\n{marker_line} "
                f"(Pozisyon: {self.head_position}, Durum: {self.current_state.name})")

