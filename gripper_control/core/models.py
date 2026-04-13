"""Core domain models for gripper control."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IndicatorColor(str, Enum):
    """UI indicator color states."""

    GREEN = "green"
    RED = "red"
    GRAY = "gray"


@dataclass(slots=True)
class GripperStatus:
    """Optional status model for future extension."""

    message: str = "Unknown"
    has_error: bool = False


@dataclass(slots=True)
class ConnectionConfig:
    """Serial connection settings."""

    port: str
    baudrate: int = 115200
    timeout: float = 1.0
    slave_id: int = 1
