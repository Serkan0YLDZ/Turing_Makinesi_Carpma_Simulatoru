from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QMessageBox,
    QSplitter, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt
from typing import Optional
from turing_simulator.domain.interfaces.ituring_machine import ITuringMachine
from turing_simulator.domain.entities.tape import Tape
from turing_simulator.domain.entities.step_result import StepResult
from turing_simulator.application.services.machine_executor import MachineExecutor
from turing_simulator.application.services.step_explainer import StepExplainer
from .controllers.execution_controller import ExecutionController
from .widgets.machine_info_widget import MachineInfoWidget
from .widgets.tape_widget import TapeWidget
from .widgets.logger_widget import LoggerWidget


class MainWindow(QMainWindow):
    
    def __init__(self, machine: ITuringMachine, parent=None):
        super().__init__(parent)
        self._machine = machine
        self._tape: Optional[Tape] = None
        
        step_explainer = StepExplainer()
        machine_executor = MachineExecutor(step_explainer)
        self._execution_controller = ExecutionController(machine_executor)
        self._execution_controller.set_machine(machine)
        
        self._setup_ui()
        self._connect_signals()
        self._load_machine_info()
    
    def _setup_ui(self) -> None:
        self.setWindowTitle("Turing Makinesi Simülatörü - f(n, m) = n × m")
        self.setGeometry(100, 100, 1800, 1000)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        top_panel = self._create_top_panel()
        main_layout.addWidget(top_panel)
        
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)
        
        tape_group = QGroupBox("Şerit Animasyonu")
        tape_group.setMinimumHeight(300)
        tape_layout = QVBoxLayout()
        self._tape_scroll = QScrollArea()
        self._tape_scroll.setWidgetResizable(True)
        self._tape_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._tape_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._tape_scroll.setMinimumHeight(280)
        self._tape_widget = TapeWidget()
        self._tape_scroll.setWidget(self._tape_widget)
        tape_layout.addWidget(self._tape_scroll)
        tape_group.setLayout(tape_layout)
        main_layout.addWidget(tape_group, 1)
        self._tape_group = tape_group
    
    def _create_top_panel(self) -> QWidget:
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        info_text = QLabel("""
        <b style="font-size: 16px; color: #2c3e50;">Fonksiyon: f(n, m) = n × m</b><br>
        <span style="color: #555;">Bu Turing makinesi, iki pozitif tam sayının çarpımını hesaplar.</span><br>
        <span style="color: #555;">Giriş: n adet '0', m adet '1' | Çıkış: n×m adet '2'</span><br>
        <span style="color: #555;">Algoritma: m'yi n kez toplama işlemi</span>
        """)
        info_text.setWordWrap(True)
        left_layout.addWidget(info_text)
        
        self._io_info = QLabel("Giriş: Henüz başlatılmadı")
        self._io_info.setStyleSheet("font-weight: bold; color: #27ae60;")
        left_layout.addWidget(self._io_info)
        
        states_group = QGroupBox("Durumların Anlamları")
        states_layout = QVBoxLayout()
        states_group.setLayout(states_layout)
        
        state_descriptions = {
            'q0': "Başlangıç durumu. Dış döngünün ilk adımını başlatır.",
            'q1': "İç döngünün ilk adımını başlatan durum.",
            'q2': "İlk 'B'yi '2'ye çevirerek sağa hareket eden durum.",
            'q3': "İç döngüde geriye dönüşü sağlayan durum.",
            'q4': "İç döngünün sonraki adımlarını başlatan; iç döngü bitti ise dış döngünün geriye dönüşünü başlatan durum.",
            'q5': "Dış döngünün geriye dönüşünü sağlayan, bu arada 1'ler öbeğine eski görünümünü kazandıran durum.",
            'q6': "Dış döngünün sonraki adımlarını başlatan durum.",
            'q7': "Bitiş konfigürasyonunda, okuma kafasının 2'ler öbeğinin başında olmasını sağlayan durumlar.",
            'q8': "Bitiş konfigürasyonunda, okuma kafasının 2'ler öbeğinin başında olmasını sağlayan durumlar.",
        }
        
        for state_name, description in state_descriptions.items():
            state_label = QLabel(f"<b>{state_name}:</b> {description}")
            state_label.setWordWrap(True)
            state_label.setStyleSheet("padding: 5px;")
            states_layout.addWidget(state_label)
        
        left_layout.addWidget(states_group)
        left_layout.addStretch()
        top_splitter.addWidget(left_panel)
        
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        machine_info_group = QGroupBox("Hareket Çizelgesi (Geçiş Tablosu)")
        machine_info_layout = QVBoxLayout()
        self._machine_info_widget = MachineInfoWidget()
        machine_info_layout.addWidget(self._machine_info_widget)
        machine_info_group.setLayout(machine_info_layout)
        right_splitter.addWidget(machine_info_group)
        
        log_group = QGroupBox("Adım Logları")
        log_layout = QVBoxLayout()
        self._logger_widget = LoggerWidget()
        log_layout.addWidget(self._logger_widget)
        log_group.setLayout(log_layout)
        right_splitter.addWidget(log_group)
        
        right_splitter.setSizes([150, 100])
        top_splitter.addWidget(right_splitter)
        
        top_splitter.setSizes([350, 350])
        top_splitter.setStretchFactor(0, 0)
        top_splitter.setStretchFactor(1, 1)
        
        return top_splitter
    
    def _create_control_panel(self) -> QWidget:
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)
        
        n_label = QLabel("n değeri:")
        layout.addWidget(n_label)
        
        self._n_input = QSpinBox()
        self._n_input.setMinimum(1)
        self._n_input.setMaximum(20)
        self._n_input.setValue(2)
        layout.addWidget(self._n_input)
        
        m_label = QLabel("m değeri:")
        layout.addWidget(m_label)
        
        self._m_input = QSpinBox()
        self._m_input.setMinimum(1)
        self._m_input.setMaximum(20)
        self._m_input.setValue(3)
        layout.addWidget(self._m_input)
        
        self._start_button = QPushButton("Başlat")
        self._start_button.clicked.connect(self._on_start_clicked)
        layout.addWidget(self._start_button)
        
        self._pause_button = QPushButton("Duraklat")
        self._pause_button.clicked.connect(self._on_pause_clicked)
        self._pause_button.setEnabled(False)
        layout.addWidget(self._pause_button)
        
        self._resume_button = QPushButton("Devam Et")
        self._resume_button.clicked.connect(self._on_resume_clicked)
        self._resume_button.setEnabled(False)
        layout.addWidget(self._resume_button)
        
        self._step_button = QPushButton("Adım Adım")
        self._step_button.clicked.connect(self._on_step_clicked)
        layout.addWidget(self._step_button)
        
        self._reset_button = QPushButton("Sıfırla")
        self._reset_button.clicked.connect(self._on_reset_clicked)
        layout.addWidget(self._reset_button)
        
        speed_label = QLabel("Hız (ms):")
        layout.addWidget(speed_label)
        
        self._speed_input = QSpinBox()
        self._speed_input.setMinimum(100)
        self._speed_input.setMaximum(5000)
        self._speed_input.setValue(500)
        self._speed_input.setSingleStep(100)
        self._speed_input.valueChanged.connect(self._on_speed_changed)
        layout.addWidget(self._speed_input)
        
        layout.addStretch()
        
        return panel
    
    def _connect_signals(self) -> None:
        self._execution_controller.step_completed.connect(self._on_step_completed)
        self._execution_controller.execution_finished.connect(
            self._on_execution_finished
        )
        self._execution_controller.execution_error.connect(self._on_execution_error)
    
    def _load_machine_info(self) -> None:
        if not self._machine:
            return
        
        transitions = self._machine.get_transitions()
        
        state_set = set()
        for (state, _), transition in transitions.items():
            state_set.add(state)
            state_set.add(transition.to_state)
        
        states = list(state_set)
        
        self._machine_info_widget.set_machine(states, transitions)
    
    def _on_start_clicked(self) -> None:
        n = self._n_input.value()
        m = self._m_input.value()
        expected_output = n * m
        
        self._tape = Tape(blank_symbol='B')
        symbols = ['0'] * n + ['1'] * m
        self._tape.initialize_from_list(symbols, start_position=0)
        
        self._io_info.setText(
            f"Giriş: n={n} ({n} adet '0'), m={m} ({m} adet '1') | "
            f"Beklenen Çıkış: n×m={expected_output} "
            f"({expected_output} adet '2')"
        )
        self._io_info.setStyleSheet("font-weight: bold; color: #3498db;")
        
        self._logger_widget.clear()
        self._logger_widget.append_text(
            f"═══════════════════════════════════════════════════════════\n"
        )
        self._logger_widget.append_text(f"Başlangıç: n = {n}, m = {m}\n")
        self._logger_widget.append_text(
            f"Fonksiyon: f(n, m) = n × m = {expected_output}\n"
        )
        self._logger_widget.append_text(
            f"═══════════════════════════════════════════════════════════\n\n"
        )
        
        self._start_button.setEnabled(False)
        self._pause_button.setEnabled(True)
        self._resume_button.setEnabled(False)
        self._step_button.setEnabled(False)
        
        self._update_tape_display()
        
        self._tape_group.raise_()
        self._tape_scroll.ensureWidgetVisible(self._tape_widget, 0, 0)
        
        self._execution_controller.start_execution(
            self._tape, 
            self._on_step_callback
        )
    
    def _on_pause_clicked(self) -> None:
        self._execution_controller.pause()
        self._pause_button.setEnabled(False)
        self._resume_button.setEnabled(True)
        self._step_button.setEnabled(True)
    
    def _on_resume_clicked(self) -> None:
        self._execution_controller.resume()
        self._pause_button.setEnabled(True)
        self._resume_button.setEnabled(False)
        self._step_button.setEnabled(False)
    
    def _on_step_clicked(self) -> None:
        result = self._execution_controller.step_once()
        if result:
            self._on_step_callback(result)
    
    def _on_reset_clicked(self) -> None:
        self._execution_controller.stop()
        self._tape = None
        self._tape_widget.update_tape({}, 0, None)
        self._logger_widget.clear()
        
        self._io_info.setText("Giriş: Henüz başlatılmadı")
        self._io_info.setStyleSheet("font-weight: bold; color: #27ae60;")
        
        self._start_button.setEnabled(True)
        self._pause_button.setEnabled(False)
        self._resume_button.setEnabled(False)
        self._step_button.setEnabled(True)
    
    def _on_speed_changed(self, value: int) -> None:
        self._execution_controller.set_speed(value)
    
    def _on_step_callback(self, result: StepResult) -> None:
        self._update_tape_display(result)
        self._logger_widget.log_step(result)
    
    def _update_tape_display(self, result: Optional[StepResult] = None) -> None:
        if result:
            self._tape_widget.update_tape(
                result.tape_snapshot,
                result.head_position,
                result.current_state.name
            )
        elif self._tape:
            self._tape_widget.update_tape(
                self._tape.get_all_symbols(),
                0,
                self._machine.get_current_state().name if self._machine else None
            )
    
    def _on_step_completed(self, result: StepResult) -> None:
        pass
    
    def _on_execution_finished(self, result: StepResult) -> None:
        self._start_button.setEnabled(True)
        self._pause_button.setEnabled(False)
        self._resume_button.setEnabled(False)
        self._step_button.setEnabled(True)
        
        if self._tape:
            twos_count = len([
                s for s in self._tape.get_all_symbols().values() 
                if s == '2'
            ])
            n = self._n_input.value()
            m = self._m_input.value()
            expected = n * m
            
            if twos_count == expected:
                self._io_info.setText(
                    f"✓ Tamamlandı! Giriş: n={n}, m={m} | "
                    f"Çıkış: {twos_count} adet '2' (Doğru: n×m={expected})"
                )
                self._io_info.setStyleSheet("font-weight: bold; color: #27ae60;")
            else:
                self._io_info.setText(
                    f"✗ Hata! Giriş: n={n}, m={m} | "
                    f"Çıkış: {twos_count} adet '2' (Beklenen: {expected})"
                )
                self._io_info.setStyleSheet("font-weight: bold; color: #e74c3c;")
            
            message = (
                f"<b>Hesaplama Tamamlandı!</b><br><br>"
                f"<b>Fonksiyon:</b> f(n, m) = n × m<br>"
                f"<b>Giriş:</b> n = {n} ({n} adet '0'), m = {m} ({m} adet '1')<br>"
                f"<b>Beklenen Çıkış:</b> n×m = {expected} ({expected} adet '2')<br>"
                f"<b>Gerçek Çıkış:</b> {twos_count} adet '2'<br><br>"
            )
            
            if twos_count == expected:
                message += (
                    "<span style='color: green; font-weight: bold;'>"
                    "✓ Sonuç DOĞRU!</span>"
                )
            else:
                message += (
                    f"<span style='color: red; font-weight: bold;'>"
                    f"✗ Sonuç YANLIŞ (beklenen: {expected})</span>"
                )
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Hesaplama Tamamlandı")
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
    
    def _on_execution_error(self, error_message: str) -> None:
        QMessageBox.critical(self, "Hata", error_message)
        self._start_button.setEnabled(True)
        self._pause_button.setEnabled(False)
        self._resume_button.setEnabled(False)
        self._step_button.setEnabled(True)

