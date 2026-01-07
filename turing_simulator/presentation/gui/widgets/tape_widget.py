from PyQt6.QtWidgets import QWidget, QScrollArea
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QPolygon
from typing import Dict, Optional


class TapeWidget(QWidget):
    
    SYMBOL_COLORS = {
        '0': QColor(100, 150, 255),
        '1': QColor(100, 200, 100),
        '2': QColor(255, 150, 100),
        'X': QColor(200, 100, 200),
        'Y': QColor(255, 200, 100),
        'B': QColor(240, 240, 240),
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tape_snapshot: Dict[int, str] = {}
        self._head_position = 0
        self._current_state: Optional[str] = None
        self._cell_size = 60
        self._visible_cells = 25
        self.setMinimumSize(1200, 200)
        self.setMaximumHeight(400)
    
    def update_tape(
        self, 
        tape_snapshot: Dict[int, str], 
        head_position: int, 
        current_state: Optional[str] = None
    ) -> None:
        self._tape_snapshot = tape_snapshot.copy()
        
        visible_min = head_position - self._visible_cells // 2
        visible_max = head_position + self._visible_cells // 2
        
        for pos in range(visible_min, visible_max + 1):
            if pos not in self._tape_snapshot:
                self._tape_snapshot[pos] = 'B'
        
        self._head_position = head_position
        self._current_state = current_state
        self.update()
        self._scroll_to_head()
    
    def _scroll_to_head(self) -> None:
        parent = self.parent()
        while parent and not isinstance(parent, QScrollArea):
            parent = parent.parent()
        
        if isinstance(parent, QScrollArea):
            cell_width = self._cell_size + 8
            scroll_x = max(
                0, 
                (self._head_position - self._visible_cells // 2) * cell_width
            )
            parent.horizontalScrollBar().setValue(int(scroll_x))
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self._tape_snapshot:
            painter.drawText(
                self.rect(), 
                Qt.AlignmentFlag.AlignCenter, 
                "Şerit başlatılmamış"
            )
            return
        
        display_min = self._head_position - self._visible_cells // 2
        display_max = self._head_position + self._visible_cells // 2
        
        x_start = 20
        y_start = 70
        
        for i, pos in enumerate(range(display_min, display_max + 1)):
            x = x_start + i * (self._cell_size + 8)
            y = y_start
            self._draw_cell(painter, x, y, pos)
        
        head_idx = self._head_position - display_min
        head_x = x_start + head_idx * (self._cell_size + 8) + self._cell_size // 2
        head_y = y_start - 35
        
        self._draw_head_arrow(painter, head_x, head_y)
        
        info_y = 10
        
        if self._current_state:
            font = QFont("Arial", 11, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor(0, 100, 0)))
            state_text = (
                f"Durum: {self._current_state} | "
                f"Pozisyon: {self._head_position}"
            )
            painter.drawText(
                20, info_y, 400, 25, 
                Qt.AlignmentFlag.AlignLeft, 
                state_text
            )
        
        stats = self._calculate_statistics()
        font_stats = QFont("Arial", 10)
        painter.setFont(font_stats)
        painter.setPen(QPen(QColor(100, 100, 100)))
        stats_text = (
            f"0'ler: {stats['zeros']} | "
            f"1'ler: {stats['ones']} | "
            f"2'ler: {stats['twos']} | "
            f"X'ler: {stats['x']} | "
            f"Y'ler: {stats['y']}"
        )
        painter.drawText(
            20, info_y + 25, 800, 20, 
            Qt.AlignmentFlag.AlignLeft, 
            stats_text
        )
    
    def _calculate_statistics(self) -> Dict[str, int]:
        stats = {
            'zeros': 0,
            'ones': 0,
            'twos': 0,
            'x': 0,
            'y': 0,
        }
        
        for symbol in self._tape_snapshot.values():
            if symbol == '0':
                stats['zeros'] += 1
            elif symbol == '1':
                stats['ones'] += 1
            elif symbol == '2':
                stats['twos'] += 1
            elif symbol == 'X':
                stats['x'] += 1
            elif symbol == 'Y':
                stats['y'] += 1
        
        return stats
    
    def _draw_cell(
        self, 
        painter: QPainter, 
        x: int, 
        y: int, 
        position: int
    ) -> None:
        pen = QPen(QColor(100, 100, 100), 2)
        painter.setPen(pen)
        
        symbol = self._tape_snapshot.get(position, 'B')
        
        if position == self._head_position:
            brush = QBrush(QColor(255, 240, 200))
        else:
            brush = QBrush(QColor(255, 255, 255))
        
        painter.setBrush(brush)
        painter.drawRect(x, y, self._cell_size, self._cell_size)
        
        if symbol == 'B':
            bg_brush = QBrush(QColor(240, 240, 240))
            painter.setBrush(bg_brush)
            painter.drawRect(
                x + 1, y + 1, 
                self._cell_size - 2, 
                self._cell_size - 2
            )
            painter.setBrush(brush)
            display_symbol = 'B'
            font = QFont("Arial", 20, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor(80, 80, 80), 3))
        else:
            display_symbol = symbol
            font = QFont("Arial", 20, QFont.Weight.Bold)
            painter.setFont(font)
            color = self.SYMBOL_COLORS.get(symbol, QColor(0, 0, 0))
            painter.setPen(QPen(color, 2))
            
            bg_color = QColor(color)
            bg_color.setAlpha(30)
            bg_brush = QBrush(bg_color)
            painter.setBrush(bg_brush)
            painter.drawRect(
                x + 1, y + 1, 
                self._cell_size - 2, 
                self._cell_size - 2
            )
            painter.setBrush(brush)
        
        painter.drawText(
            x, y, self._cell_size, self._cell_size,
            Qt.AlignmentFlag.AlignCenter, 
            display_symbol
        )
        
        font_small = QFont("Arial", 9, QFont.Weight.Bold)
        painter.setFont(font_small)
        painter.setPen(QPen(QColor(80, 80, 80)))
        painter.drawText(
            x, y + self._cell_size + 18, 
            self._cell_size, 18,
            Qt.AlignmentFlag.AlignCenter, 
            str(position)
        )
    
    def _draw_head_arrow(self, painter: QPainter, x: int, y: int) -> None:
        pen = QPen(QColor(255, 50, 50), 4)
        painter.setPen(pen)
        
        painter.drawLine(x, y, x, y + 25)
        
        arrow_size = 10
        painter.drawLine(x, y, x - arrow_size, y + arrow_size)
        painter.drawLine(x, y, x + arrow_size, y + arrow_size)
        
        brush = QBrush(QColor(255, 50, 50))
        painter.setBrush(brush)
        points = [
            QPoint(x, y),
            QPoint(x - arrow_size, y + arrow_size),
            QPoint(x + arrow_size, y + arrow_size)
        ]
        polygon = QPolygon(points)
        painter.drawPolygon(polygon)
