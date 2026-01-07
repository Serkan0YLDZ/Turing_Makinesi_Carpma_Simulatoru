from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    name: str
    is_initial: bool = False
    is_final: bool = False
    description: str = ""
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return (f"State(name='{self.name}', initial={self.is_initial}, "
                f"final={self.is_final})")

