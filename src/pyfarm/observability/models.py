"""Data models for observability."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Result of a health check."""
    component: str
    status: HealthStatus
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = ""
    metrics: dict = field(default_factory=dict)


@dataclass
class LogEntry:
    """A structured log entry."""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    grow_id: str = ""
    level: str = "info"
    component: str = ""
    message: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Metric:
    """A time-series metric."""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    name: str = ""
    value: float = 0.0
    unit: str = ""
    tags: dict = field(default_factory=dict)
