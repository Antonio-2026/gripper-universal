"""Main PyQt5 window for universal gripper control."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from gripper_control.core.models import IndicatorColor


class MainWindow(QMainWindow):
    """Presentation-only UI layer. Business logic is injected via signals."""

    connect_clicked = pyqtSignal()
    initialize_clicked = pyqtSignal()
    open_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    position_changed = pyqtSignal(int)
    force_changed = pyqtSignal(int)
    speed_changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Universal Gripper Control")
        self.resize(680, 420)

        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)

        main_layout.addWidget(self._build_controls_group())
        main_layout.addWidget(self._build_action_group())
        main_layout.addWidget(self._build_status_group())

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _build_controls_group(self) -> QGroupBox:
        box = QGroupBox("Motion & Force Controls")
        layout = QGridLayout(box)

        self.position_slider = self._make_slider(0, 100, 0)
        self.force_slider = self._make_slider(20, 100, 20)
        self.speed_slider = self._make_slider(0, 100, 30)

        self.position_label = QLabel("Position: 0%")
        self.force_label = QLabel("Force: 20%")
        self.speed_label = QLabel("Speed: 30%")

        self.position_slider.valueChanged.connect(self._on_position_slider)
        self.force_slider.valueChanged.connect(self._on_force_slider)
        self.speed_slider.valueChanged.connect(self._on_speed_slider)

        layout.addWidget(self.position_label, 0, 0)
        layout.addWidget(self.position_slider, 0, 1)

        layout.addWidget(self.force_label, 1, 0)
        layout.addWidget(self.force_slider, 1, 1)

        layout.addWidget(self.speed_label, 2, 0)
        layout.addWidget(self.speed_slider, 2, 1)

        return box

    def _build_action_group(self) -> QGroupBox:
        box = QGroupBox("Actions")
        layout = QHBoxLayout(box)

        self.connect_btn = QPushButton("Connect")
        self.initialize_btn = QPushButton("Initialize")
        self.open_btn = QPushButton("Open")
        self.close_btn = QPushButton("Close")

        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        self.initialize_btn.clicked.connect(self.initialize_clicked.emit)
        self.open_btn.clicked.connect(self.open_clicked.emit)
        self.close_btn.clicked.connect(self.close_clicked.emit)

        for btn in [self.connect_btn, self.initialize_btn, self.open_btn, self.close_btn]:
            btn.setMinimumHeight(40)
            layout.addWidget(btn)

        return box

    def _build_status_group(self) -> QGroupBox:
        box = QGroupBox("Status")
        layout = QHBoxLayout(box)

        self.indicator = QLabel("●")
        self.indicator.setStyleSheet("font-size: 28px; color: gray;")
        self.status_label = QLabel("Disconnected")
        self.status_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        layout.addWidget(self.indicator)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        return box

    def _make_slider(self, minimum: int, maximum: int, value: int) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        return slider

    def _on_position_slider(self, value: int) -> None:
        self.position_label.setText(f"Position: {value}%")
        self.position_changed.emit(value)

    def _on_force_slider(self, value: int) -> None:
        self.force_label.setText(f"Force: {value}%")
        self.force_changed.emit(value)

    def _on_speed_slider(self, value: int) -> None:
        self.speed_label.setText(f"Speed: {value}%")
        self.speed_changed.emit(value)

    def set_status(self, text: str, color: IndicatorColor) -> None:
        palette = {
            IndicatorColor.GREEN: QColor("#2ecc71").name(),
            IndicatorColor.BLUE: QColor("#3498db").name(),
            IndicatorColor.RED: QColor("#e74c3c").name(),
            IndicatorColor.GRAY: QColor("#9e9e9e").name(),
        }
        self.indicator.setStyleSheet(f"font-size: 28px; color: {palette[color]};")
        self.status_label.setText(text)
        self.status_bar.showMessage(text)
