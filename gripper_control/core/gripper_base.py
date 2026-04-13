"""Abstract contract for all electric gripper drivers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from gripper_control.core.models import GripperStatus


class GripperError(Exception):
    """Base exception for gripper operations."""


class ConnectionError(GripperError):
    """Raised when connection operations fail."""


class CommandError(GripperError):
    """Raised when a device command cannot be executed."""


class GripperBase(ABC):
    """Base class for all gripper drivers (DH, SMC, Robotiq, OnRobot, ...)."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the physical gripper."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the physical gripper."""

    @abstractmethod
    def initialize(self) -> None:
        """Run gripper initialization/calibration sequence."""

    @abstractmethod
    def open(self) -> None:
        """Open the gripper jaws."""

    @abstractmethod
    def close(self) -> None:
        """Close the gripper jaws."""

    @abstractmethod
    def set_position(self, value: int) -> None:
        """Set target position."""

    @abstractmethod
    def set_force(self, value: int) -> None:
        """Set gripping force."""

    @abstractmethod
    def set_speed(self, value: int) -> None:
        """Set jaw movement speed."""

    @abstractmethod
    def get_status(self) -> GripperStatus:
        """Read and return current gripper status."""

    @staticmethod
    def _validate_range(name: str, value: int, min_value: int, max_value: int) -> None:
        if not min_value <= value <= max_value:
            raise CommandError(f"{name}={value} is out of range [{min_value}, {max_value}].")

    @staticmethod
    def _require(condition: bool, message: str, exc_type: type[Exception] = GripperError) -> None:
        if not condition:
            raise exc_type(message)

    @staticmethod
    def _safe_value(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
