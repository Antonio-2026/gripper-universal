"""Core domain models for gripper control."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IndicatorColor(str, Enum):
    """UI indicator color states."""

    GREEN = "green"
    BLUE = "blue"
    RED = "red"
    GRAY = "gray"


@dataclass(slots=True)
class GripperStatus:
    """Unified status object for all gripper drivers."""

    raw_status: int
    is_ready: bool = False
    object_detected: bool = False
    has_error: bool = False
    message: str = "Unknown"


@dataclass(slots=True)
class ConnectionConfig:
    """Serial/fieldbus connection settings."""

    port: str
    baudrate: int = 115200
    timeout: float = 0.5
    slave_id: int = 1
