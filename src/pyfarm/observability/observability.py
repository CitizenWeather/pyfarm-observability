"""Main observability interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pyfarm.observability.models import HealthCheck, LogEntry, Metric


class Observability(ABC):
    """Interface for observability services."""

    @abstractmethod
    async def log(self, entry: LogEntry) -> None:
        """Log a structured entry."""
        pass

    @abstractmethod
    async def record_metric(self, metric: Metric) -> None:
        """Record a metric value."""
        pass

    @abstractmethod
    async def check_health(self, component: str) -> HealthCheck:
        """Check health of a component."""
        pass

    @abstractmethod
    async def query_logs(
        self,
        grow_id: str,
        component: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Query historical logs."""
        pass

    @abstractmethod
    async def query_metrics(
        self,
        name: str,
        limit: int = 100,
    ) -> list[Metric]:
        """Query historical metrics."""
        pass
