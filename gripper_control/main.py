"""Application entry point for the universal gripper control platform."""

from __future__ import annotations

import argparse
import sys
from typing import Callable

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from gripper_control.core.gripper_base import GripperError
from gripper_control.core.models import ConnectionConfig, IndicatorColor
from gripper_control.drivers.dh_modbus import DHModbusGripper
from gripper_control.ui.main_window import MainWindow
from gripper_control.utils.logger import configure_logging, get_logger


class GripperController:
    """Application logic layer wiring the UI and the gripper driver."""

    def __init__(self, window: MainWindow, driver: DHModbusGripper) -> None:
        self.window = window
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)
        self._connected = False

        self.window.connect_clicked.connect(self.connect)
        self.window.initialize_clicked.connect(self.initialize)
        self.window.open_clicked.connect(self.open)
        self.window.close_clicked.connect(self.close)

        self.window.position_changed.connect(self.on_position_changed)
        self.window.force_changed.connect(self.on_force_changed)
        self.window.speed_changed.connect(self.on_speed_changed)

        self.status_timer = QTimer(self.window)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start(500)

    def connect(self) -> None:
        self._run_safe("Connect", self.driver.connect)
        self._connected = True
        self.window.set_status("Connected", IndicatorColor.BLUE)

    def initialize(self) -> None:
        self._run_safe("Initialize", self.driver.initialize)
        self.window.set_status("Initialized", IndicatorColor.BLUE)

    def open(self) -> None:
        self._run_safe("Open", self.driver.open)
        self.window.set_status("Open command sent", IndicatorColor.BLUE)

    def close(self) -> None:
        self._run_safe("Close", self.driver.close)
        self.window.set_status("Close command sent", IndicatorColor.BLUE)

    def on_position_changed(self, ui_value: int) -> None:
        if not self._connected:
            return
        # UI uses 0-100%; DH register expects 0-1000.
        position = int(ui_value * 10)
        self._run_safe("Set position", lambda: self.driver.set_position(position), update_status=False)

    def on_force_changed(self, value: int) -> None:
        if not self._connected:
            return
        self._run_safe("Set force", lambda: self.driver.set_force(value), update_status=False)

    def on_speed_changed(self, ui_value: int) -> None:
        if not self._connected:
            return
        speed = max(1, ui_value)
        self._run_safe("Set speed", lambda: self.driver.set_speed(speed), update_status=False)

    def refresh_status(self) -> None:
        if not self._connected:
            return
        try:
            status = self.driver.get_status()
        except GripperError as exc:
            self.logger.debug("Status refresh failed: %s", exc)
            return

        color = IndicatorColor.BLUE
        if status.has_error:
            color = IndicatorColor.RED
        elif status.object_detected:
            color = IndicatorColor.GREEN

        self.window.set_status(status.message, color)

    def _run_safe(self, action: str, fn: Callable[[], None], update_status: bool = True) -> None:
        try:
            fn()
            if update_status:
                self.window.set_status(f"{action} successful", IndicatorColor.BLUE)
        except GripperError as exc:
            self.logger.exception("%s failed", action)
            self.window.set_status(f"{action} failed: {exc}", IndicatorColor.RED)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Universal electric gripper control")
    parser.add_argument("--port", default="COM3", help="Serial COM/tty port (example: COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Modbus RTU baudrate")
    parser.add_argument("--slave-id", type=int, default=1, help="Modbus slave address")
    parser.add_argument("--timeout", type=float, default=0.5, help="Communication timeout in seconds")
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()

    app = QApplication(sys.argv)
    window = MainWindow()

    cfg = ConnectionConfig(
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
        slave_id=args.slave_id,
    )
    driver = DHModbusGripper(cfg)
    GripperController(window, driver)

    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
