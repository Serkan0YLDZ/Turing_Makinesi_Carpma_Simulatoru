from abc import ABC, abstractmethod
from typing import Dict, Tuple


class ITape(ABC):
    
    @abstractmethod
    def read(self, position: int) -> str:
        pass
    
    @abstractmethod
    def write(self, position: int, symbol: str) -> None:
        pass
    
    @abstractmethod
    def get_visible_range(self) -> Tuple[int, int]:
        pass
    
    @abstractmethod
    def get_all_symbols(self) -> Dict[int, str]:
        pass
    
    @abstractmethod
    def get_symbol_at_range(self, min_pos: int, max_pos: int) -> Dict[int, str]:
        pass

