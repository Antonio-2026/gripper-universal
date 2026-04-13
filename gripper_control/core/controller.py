"""Application controller for coordinating UI actions and driver calls."""

from __future__ import annotations

from typing import Optional

from gripper_control.core.models import ConnectionConfig, IndicatorColor
from gripper_control.drivers.py_modbus_gripper import DHModbusGripper
from gripper_control.ui.main_window import MainWindow


class GripperController:
    """Controller that binds user interactions to gripper driver commands."""

    def __init__(self, window: MainWindow) -> None:
        self.window = window
        self.driver: Optional[DHModbusGripper] = None
        self._connected = False

        self.window.connect_clicked.connect(self.connect)
        self.window.initialize_clicked.connect(self.initialize)
        self.window.open_clicked.connect(self.open)
        self.window.close_clicked.connect(self.close)

    def log(self, message: str) -> None:
        self.window.append_log(message)

    def connect(self) -> None:
        port, baudrate, slave_id = self.window.read_connection_values()
        self.log(f"Connecting to {port} @ {baudrate}")

        config = ConnectionConfig(port=port, baudrate=baudrate, slave_id=slave_id, timeout=1.0)
        self.driver = DHModbusGripper(config)

        try:
            if self.driver.connect():
                self._connected = True
                self.window.set_status("Connected", IndicatorColor.GREEN)
                self.log("Connection established")
                return

            self._connected = False
            self.window.set_status("Connection failed", IndicatorColor.RED)
            self.log("Connection failed")
        except Exception as exc:  # hardware-safe guard
            self._connected = False
            self.window.set_status("Connection error", IndicatorColor.RED)
            self.log(f"Connection error: {exc}")

    def initialize(self) -> None:
        self._run_hardware_call("Initialize", lambda: self.driver.initialize() if self.driver else None)

    def open(self) -> None:
        self._run_hardware_call(
            "Open",
            lambda: self.driver.open(
                position=self.window.position_value(),
                force=self.window.force_value(),
                speed=self.window.speed_value(),
            )
            if self.driver
            else None,
        )

    def close(self) -> None:
        self._run_hardware_call(
            "Close",
            lambda: self.driver.close(
                force=self.window.force_value(),
                speed=self.window.speed_value(),
            )
            if self.driver
            else None,
        )

    def _run_hardware_call(self, action: str, call) -> None:
        if not self._connected or self.driver is None:
            self.log(f"{action}: not connected")
            self.window.set_status("Disconnected", IndicatorColor.GRAY)
            return

        try:
            call()
            self.log(f"{action} action sent")
        except Exception as exc:  # hardware-safe guard
            self.window.set_status("Error", IndicatorColor.RED)
            self.log(f"{action} error: {exc}")
