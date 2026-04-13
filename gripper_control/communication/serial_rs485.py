"""Low-level RS485 serial helper with timeout and auto-reconnect support."""

from __future__ import annotations

import time
from typing import Optional

import serial
from serial import SerialException

from gripper_control.utils.logger import get_logger


class SerialRS485:
    """Simple RS485 wrapper around pyserial."""

    def __init__(self, reconnect_attempts: int = 3, reconnect_delay: float = 0.4) -> None:
        self._logger = get_logger(self.__class__.__name__)
        self._serial: Optional[serial.Serial] = None
        self._port: Optional[str] = None
        self._baudrate: int = 115200
        self._timeout: float = 0.5
        self._reconnect_attempts = reconnect_attempts
        self._reconnect_delay = reconnect_delay

    @property
    def is_open(self) -> bool:
        return bool(self._serial and self._serial.is_open)

    def open(self, port: str, baudrate: int = 115200, timeout: float = 0.5) -> None:
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._logger.info("Opening RS485 port=%s baudrate=%s timeout=%s", port, baudrate, timeout)

        self.close()
        self._serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=timeout,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
        )

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._logger.info("Closed RS485 serial port")

    def send(self, data: bytes) -> int:
        self._ensure_connection()
        assert self._serial is not None
        return self._serial.write(data)

    def receive(self, size: int = 256) -> bytes:
        self._ensure_connection()
        assert self._serial is not None
        return self._serial.read(size)

    def _ensure_connection(self) -> None:
        if self.is_open:
            return

        if not self._port:
            raise SerialException("Serial port is not configured.")

        for attempt in range(1, self._reconnect_attempts + 1):
            try:
                self._logger.warning("RS485 disconnected. Reconnecting attempt %s/%s", attempt, self._reconnect_attempts)
                self.open(self._port, self._baudrate, self._timeout)
                return
            except SerialException:
                if attempt >= self._reconnect_attempts:
                    raise
                time.sleep(self._reconnect_delay)
