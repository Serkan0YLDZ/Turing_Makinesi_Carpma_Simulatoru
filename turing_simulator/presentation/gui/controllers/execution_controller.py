from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from typing import Optional, Callable
from turing_simulator.domain.interfaces.ituring_machine import ITuringMachine
from turing_simulator.domain.interfaces.itape import ITape
from turing_simulator.domain.entities.step_result import StepResult
from turing_simulator.application.services.machine_executor import MachineExecutor


class ExecutionController(QObject):
    
    step_completed = pyqtSignal(StepResult)
    execution_finished = pyqtSignal(StepResult)
    execution_error = pyqtSignal(str)
    
    def __init__(self, machine_executor: MachineExecutor):
        super().__init__()
        self._machine_executor = machine_executor
        self._machine: Optional[ITuringMachine] = None
        self._tape: Optional[ITape] = None
        self._timer: Optional[QTimer] = None
        self._is_running = False
        self._is_paused = False
        self._step_delay_ms = 500
    
    def set_machine(self, machine: ITuringMachine) -> None:
        self._machine = machine
    
    def set_speed(self, delay_ms: int) -> None:
        self._step_delay_ms = delay_ms
        if self._timer:
            self._timer.setInterval(delay_ms)
    
    def start_execution(
        self, 
        initial_tape: ITape, 
        step_callback: Optional[Callable[[StepResult], None]] = None
    ) -> None:
        if not self._machine:
            self.execution_error.emit("Makine tanımlanmamış")
            return
        
        if self._is_running:
            self.execution_error.emit("Makine zaten çalışıyor")
            return
        
        self._tape = initial_tape
        self._machine.reset(initial_tape)
        self._is_running = True
        self._is_paused = False
        
        self._timer = QTimer()
        self._timer.timeout.connect(
            lambda: self._execute_step(step_callback)
        )
        self._timer.setInterval(self._step_delay_ms)
        self._timer.start()
    
    def _execute_step(
        self, 
        step_callback: Optional[Callable[[StepResult], None]] = None
    ) -> None:
        if not self._machine or not self._is_running or self._is_paused:
            return
        
        try:
            result = self._machine_executor.step_with_explanation(self._machine)
            self.step_completed.emit(result)
            
            if step_callback:
                step_callback(result)
            
            if result.is_halted:
                self._stop_execution()
                self.execution_finished.emit(result)
        except RuntimeError as e:
            self._stop_execution()
            self.execution_error.emit(str(e))
    
    def pause(self) -> None:
        self._is_paused = True
    
    def resume(self) -> None:
        self._is_paused = False
    
    def stop(self) -> None:
        self._stop_execution()
    
    def _stop_execution(self) -> None:
        self._is_running = False
        self._is_paused = False
        if self._timer:
            self._timer.stop()
            self._timer = None
    
    def step_once(self) -> Optional[StepResult]:
        if not self._machine:
            self.execution_error.emit("Makine tanımlanmamış")
            return None
        
        if self._machine.is_halted():
            self.execution_error.emit("Makine zaten durmuş")
            return None
        
        try:
            result = self._machine_executor.step_with_explanation(self._machine)
            self.step_completed.emit(result)
            
            if result.is_halted:
                self.execution_finished.emit(result)
            
            return result
        except RuntimeError as e:
            self.execution_error.emit(str(e))
            return None
    
    def is_running(self) -> bool:
        return self._is_running
    
    def is_paused(self) -> bool:
        return self._is_paused
