"""DH Robotics electric gripper driver over Modbus RTU."""

from __future__ import annotations

import time

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

from gripper_control.core.gripper_base import CommandError, ConnectionError, GripperBase
from gripper_control.core.models import ConnectionConfig, GripperStatus
from gripper_control.utils.logger import get_logger


class DHModbusGripper(GripperBase):
    """DH Robotics gripper controller using Modbus RTU registers."""

    REG_INIT = 0x0100
    REG_FORCE = 0x0101
    REG_POSITION = 0x0103
    REG_SPEED = 0x0104
    REG_STATUS = 0x0201

    def __init__(
        self,
        config: ConnectionConfig,
        reconnect_attempts: int = 3,
        reconnect_delay: float = 0.4,
    ) -> None:
        self.config = config
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self._logger = get_logger(self.__class__.__name__)
        self._client = ModbusSerialClient(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
            method="rtu",
            stopbits=1,
            bytesize=8,
            parity="N",
        )
        self._connected = False

    def connect(self) -> None:
        for attempt in range(1, self.reconnect_attempts + 1):
            if self._client.connect():
                self._connected = True
                self._logger.info("Connected to DH gripper on %s", self.config.port)
                return
            self._logger.warning("Connect attempt %s/%s failed", attempt, self.reconnect_attempts)
            time.sleep(self.reconnect_delay)
        raise ConnectionError(f"Unable to connect to gripper at port {self.config.port}.")

    def disconnect(self) -> None:
        self._client.close()
        self._connected = False
        self._logger.info("Disconnected from DH gripper")

    def initialize(self) -> None:
        self._write_register(self.REG_INIT, 1)

    def open(self) -> None:
        self.set_position(0)

    def close(self) -> None:
        self.set_position(1000)

    def set_position(self, value: int) -> None:
        self._validate_range("position", value, 0, 1000)
        self._write_register(self.REG_POSITION, value)

    def set_force(self, value: int) -> None:
        self._validate_range("force", value, 20, 100)
        self._write_register(self.REG_FORCE, value)

    def set_speed(self, value: int) -> None:
        self._validate_range("speed", value, 1, 100)
        self._write_register(self.REG_SPEED, value)

    def get_status(self) -> GripperStatus:
        raw = self._read_register(self.REG_STATUS)

        # Generic status mapping. Adjust bit masks as model documentation evolves.
        has_error = bool(raw & 0b0001)
        is_ready = bool(raw & 0b0010)
        object_detected = bool(raw & 0b0100)

        if has_error:
            msg = "Error"
        elif object_detected:
            msg = "Object detected"
        elif is_ready:
            msg = "Ready"
        else:
            msg = "Busy"

        return GripperStatus(
            raw_status=raw,
            is_ready=is_ready,
            object_detected=object_detected,
            has_error=has_error,
            message=msg,
        )

    def _read_register(self, address: int) -> int:
        response = self._with_reconnect(lambda: self._client.read_holding_registers(address=address, count=1, device_id=self.config.slave_id))
        if response.isError():
            raise CommandError(f"Read failed for register 0x{address:04X}: {response}")
        return int(response.registers[0])

    def _write_register(self, address: int, value: int) -> None:
        response = self._with_reconnect(lambda: self._client.write_register(address=address, value=value, device_id=self.config.slave_id))
        if response.isError():
            raise CommandError(f"Write failed for register 0x{address:04X}: {response}")

    def _with_reconnect(self, operation):
        self._require(self._connected, "Gripper is not connected.", ConnectionError)

        for attempt in range(1, self.reconnect_attempts + 1):
            try:
                return operation()
            except ModbusException as exc:
                self._logger.warning("Modbus operation failed (%s/%s): %s", attempt, self.reconnect_attempts, exc)
                if attempt >= self.reconnect_attempts:
                    raise CommandError("Modbus communication failed after retries.") from exc
                self._reconnect()
                time.sleep(self.reconnect_delay)

        raise CommandError("Unreachable reconnect error state.")

    def _reconnect(self) -> None:
        self._client.close()
        self._connected = bool(self._client.connect())
        if not self._connected:
            raise ConnectionError("Reconnection attempt failed.")
