from typing import Dict, Tuple
from ..interfaces.itape import ITape


class Tape(ITape):
    
    def __init__(self, blank_symbol: str = 'B'):
        self._cells: Dict[int, str] = {}
        self._blank_symbol = blank_symbol
        self._min_position = 0
        self._max_position = 0
    
    def read(self, position: int) -> str:
        return self._cells.get(position, self._blank_symbol)
    
    def write(self, position: int, symbol: str) -> None:
        if symbol == self._blank_symbol:
            if position in self._cells:
                del self._cells[position]
        else:
            self._cells[position] = symbol
        
        self._update_range()
    
    def _update_range(self) -> None:
        if self._cells:
            self._min_position = min(self._cells.keys())
            self._max_position = max(self._cells.keys())
        else:
            self._min_position = 0
            self._max_position = 0
    
    def get_visible_range(self) -> Tuple[int, int]:
        if not self._cells:
            return (0, 0)
        return (self._min_position, self._max_position)
    
    def get_all_symbols(self) -> Dict[int, str]:
        return self._cells.copy()
    
    def get_symbol_at_range(self, min_pos: int, max_pos: int) -> Dict[int, str]:
        result = {}
        for pos in range(min_pos, max_pos + 1):
            symbol = self.read(pos)
            if symbol != self._blank_symbol:
                result[pos] = symbol
        return result
    
    def initialize_from_list(self, symbols: list, start_position: int = 0) -> None:
        self._cells.clear()
        for i, symbol in enumerate(symbols):
            if symbol != self._blank_symbol:
                self._cells[start_position + i] = symbol
        self._update_range()
    
    def get_blank_symbol(self) -> str:
        return self._blank_symbol

