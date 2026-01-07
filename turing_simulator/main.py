import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication
from turing_simulator.domain.machines.machine_multiply import create_multiply_machine
from turing_simulator.presentation.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Turing Makinesi Simülatörü - Çarpma")
    
    machine = create_multiply_machine()
    window = MainWindow(machine)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

