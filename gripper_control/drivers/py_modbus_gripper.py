"""Modbus RTU driver wrapper for universal gripper actions."""

from __future__ import annotations

from pymodbus.client import ModbusSerialClient

from gripper_control.core.models import ConnectionConfig


class DHModbusGripper:
    """Minimal DH-style Modbus gripper driver with safe command methods."""

    REG_INIT = 0x0100
    REG_FORCE = 0x0101
    REG_POSITION = 0x0103
    REG_SPEED = 0x0104

    def __init__(self, config: ConnectionConfig) -> None:
        self.config = config
        self.client = ModbusSerialClient(
            port=config.port,
            baudrate=config.baudrate,
            parity="N",
            stopbits=1,
            bytesize=8,
            timeout=config.timeout,
        )

    def connect(self) -> bool:
        """Open serial connection."""

        return bool(self.client.connect())

    def initialize(self) -> None:
        self._write_register(self.REG_INIT, 1)

    def open(self, position: int, force: int, speed: int) -> None:
        self._write_register(self.REG_FORCE, int(force))
        self._write_register(self.REG_SPEED, int(speed))
        self._write_register(self.REG_POSITION, int(position) * 10)

    def close(self, force: int, speed: int) -> None:
        self._write_register(self.REG_FORCE, int(force))
        self._write_register(self.REG_SPEED, int(speed))
        self._write_register(self.REG_POSITION, 1000)

    def _write_register(self, register: int, value: int) -> None:
        response = self.client.write_register(address=register, value=value, device_id=self.config.slave_id)
        if response.isError():
            raise RuntimeError(f"Modbus write failed at 0x{register:04X}: {response}")
