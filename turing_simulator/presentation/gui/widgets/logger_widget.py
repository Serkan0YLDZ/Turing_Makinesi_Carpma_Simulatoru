from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt
from typing import Optional
from turing_simulator.domain.entities.step_result import StepResult


class LoggerWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFontFamily("Courier")
        self._log_text.setFontPointSize(9)
        layout.addWidget(self._log_text)
    
    def log_step(self, step_result: StepResult) -> None:
        log_text = self._format_step_result(step_result)
        self._log_text.append(log_text)
        
        scrollbar = self._log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _format_step_result(self, step_result: StepResult) -> str:
        lines = [
            f"{'='*70}",
            f"Adım {step_result.step_number}",
            f"{'='*70}",
        ]
        
        if step_result.explanation:
            lines.append(step_result.explanation)
        else:
            lines.extend([
                f"Durum Geçişi: {step_result.previous_state.name} → "
                f"{step_result.current_state.name}",
                f"Okunan Sembol: '{step_result.read_symbol}'",
                f"Yazılan Sembol: '{step_result.write_symbol}'",
                f"Hareket Yönü: "
                f"{'Sol' if step_result.direction == 'L' else 'Sağ' if step_result.direction == 'R' else 'Yok'}",
                f"Kafa Pozisyonu: {step_result.head_position}",
            ])
        
        if step_result.is_halted:
            lines.append("")
            lines.append("*** MAKİNE DURDU ***")
        
        lines.append("")
        return "\n".join(lines)
    
    def clear(self) -> None:
        self._log_text.clear()
    
    def append_text(self, text: str) -> None:
        self._log_text.append(text)
