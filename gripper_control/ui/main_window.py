"""PyQt5 main window for the Universal Gripper Control desktop app."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gripper_control.core.models import IndicatorColor


class MainWindow(QMainWindow):
    """UI layer with no direct hardware logic."""

    connect_clicked = pyqtSignal()
    initialize_clicked = pyqtSignal()
    open_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Universal Gripper Control")
        self.resize(820, 580)

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        layout.addWidget(self._build_connection_section())
        layout.addWidget(self._build_motion_section())
        layout.addWidget(self._build_action_buttons())
        layout.addWidget(self._build_status_section())
        layout.addWidget(self._build_log_section(), stretch=1)

    def _build_connection_section(self) -> QGroupBox:
        group = QGroupBox("Connection")
        form = QFormLayout(group)

        self.port_combo = QComboBox()
        self.port_combo.addItems([f"COM{i}" for i in range(1, 11)])
        self.port_combo.setCurrentText("COM3")

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("115200")

        self.slave_spin = QSpinBox()
        self.slave_spin.setRange(1, 247)
        self.slave_spin.setValue(1)

        form.addRow("COM Port", self.port_combo)
        form.addRow("Baudrate", self.baud_combo)
        form.addRow("Slave ID", self.slave_spin)
        return group

    def _build_motion_section(self) -> QGroupBox:
        group = QGroupBox("Motion Controls")
        form = QFormLayout(group)

        self.position_slider = self._slider()
        self.force_slider = self._slider(50)
        self.speed_slider = self._slider(50)

        self.position_value_label = QLabel("50%")
        self.force_value_label = QLabel("50%")
        self.speed_value_label = QLabel("50%")

        self.position_slider.valueChanged.connect(lambda v: self.position_value_label.setText(f"{v}%"))
        self.force_slider.valueChanged.connect(lambda v: self.force_value_label.setText(f"{v}%"))
        self.speed_slider.valueChanged.connect(lambda v: self.speed_value_label.setText(f"{v}%"))

        form.addRow(self._line_with_value("Position", self.position_value_label), self.position_slider)
        form.addRow(self._line_with_value("Force", self.force_value_label), self.force_slider)
        form.addRow(self._line_with_value("Speed", self.speed_value_label), self.speed_slider)

        return group

    def _build_action_buttons(self) -> QGroupBox:
        group = QGroupBox("Actions")
        row = QHBoxLayout(group)

        self.connect_button = QPushButton("Connect")
        self.initialize_button = QPushButton("Initialize")
        self.open_button = QPushButton("Open")
        self.close_button = QPushButton("Close")

        self.connect_button.clicked.connect(self.connect_clicked.emit)
        self.initialize_button.clicked.connect(self.initialize_clicked.emit)
        self.open_button.clicked.connect(self.open_clicked.emit)
        self.close_button.clicked.connect(self.close_clicked.emit)

        for button in [self.connect_button, self.initialize_button, self.open_button, self.close_button]:
            button.setMinimumHeight(36)
            row.addWidget(button)

        return group

    def _build_status_section(self) -> QGroupBox:
        group = QGroupBox("Status")
        row = QHBoxLayout(group)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("font-size: 24px; color: #9E9E9E;")
        self.status_text = QLabel("Disconnected")

        row.addWidget(self.status_dot)
        row.addWidget(self.status_text)
        row.addStretch(1)
        return group

    def _build_log_section(self) -> QGroupBox:
        group = QGroupBox("Log")
        wrapper = QVBoxLayout(group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        wrapper.addWidget(self.log_text)
        return group

    def read_connection_values(self) -> tuple[str, int, int]:
        return self.port_combo.currentText(), int(self.baud_combo.currentText()), int(self.slave_spin.value())

    def position_value(self) -> int:
        return int(self.position_slider.value())

    def force_value(self) -> int:
        return int(self.force_slider.value())

    def speed_value(self) -> int:
        return int(self.speed_slider.value())

    def set_status(self, label: str, color: IndicatorColor) -> None:
        palette = {
            IndicatorColor.GREEN: "#2ECC71",
            IndicatorColor.RED: "#E53935",
            IndicatorColor.GRAY: "#9E9E9E",
        }
        self.status_dot.setStyleSheet(f"font-size: 24px; color: {palette[color]};")
        self.status_text.setText(label)

    def append_log(self, message: str) -> None:
        self.log_text.append(message)

    @staticmethod
    def _slider(value: int = 50) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(value)
        return slider

    @staticmethod
    def _line_with_value(label: str, value: QLabel) -> QWidget:
        holder = QWidget()
        row = QHBoxLayout(holder)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(QLabel(label))
        row.addStretch(1)
        row.addWidget(value)
        return holder
