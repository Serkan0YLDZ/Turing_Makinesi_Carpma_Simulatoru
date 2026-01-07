from dataclasses import dataclass
from .state import State


@dataclass(frozen=True)
class Transition:
    from_state: State
    to_state: State
    read_symbol: str
    write_symbol: str
    direction: str
    
    def __str__(self) -> str:
        return (f"{self.from_state.name} --[{self.read_symbol}/{self.write_symbol}, "
                f"{self.direction}]--> {self.to_state.name}")
    
    def __repr__(self) -> str:
        return (f"Transition(from_state={self.from_state.name}, "
                f"to_state={self.to_state.name}, read='{self.read_symbol}', "
                f"write='{self.write_symbol}', dir='{self.direction}')")

