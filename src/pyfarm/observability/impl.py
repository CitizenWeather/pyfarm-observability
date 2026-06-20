"""Complete observability implementation."""

from __future__ import annotations

from typing import Optional

from pyfarm.core.models import ControlEvent
from pyfarm.observability.event_bus import EventBus
from pyfarm.observability.health import HealthMonitor
from pyfarm.observability.log_store import LogStore
from pyfarm.observability.models import HealthCheck, LogEntry, Metric
from pyfarm.observability.observability import Observability


class ObservabilityImpl(Observability):
    """Complete observability implementation with logging, metrics, health checks."""

    def __init__(
        self,
        max_logs_per_grow: int = 10000,
        log_ttl_hours: int = 168,
        stale_threshold_seconds: int = 60,
    ):
        """Initialize observability system.

        Args:
            max_logs_per_grow: Max log entries per grow
            log_ttl_hours: Log retention time in hours
            stale_threshold_seconds: Data staleness threshold
        """
        self._log_store = LogStore(max_logs_per_grow, log_ttl_hours)
        self._health_monitor = HealthMonitor(stale_threshold_seconds)
        self._event_bus = EventBus()
        self._metrics: dict[str, list[Metric]] = {}

    async def log(self, entry: LogEntry) -> None:
        """Log a structured entry."""
        await self._log_store.write(entry)

    async def record_metric(self, metric: Metric) -> None:
        """Record a metric value."""
        if metric.name not in self._metrics:
            self._metrics[metric.name] = []
        self._metrics[metric.name].append(metric)

        # Keep only last 1000 values per metric
        if len(self._metrics[metric.name]) > 1000:
            self._metrics[metric.name] = self._metrics[metric.name][-1000:]

    async def check_health(self, component: str) -> HealthCheck:
        """Check health of a component."""
        return await self._health_monitor.check_health(component)

    async def query_logs(
        self,
        grow_id: str,
        component: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Query historical logs."""
        return await self._log_store.query(grow_id, component, level, limit)

    async def query_metrics(
        self,
        name: str,
        limit: int = 100,
    ) -> list[Metric]:
        """Query historical metrics."""
        metrics = self._metrics.get(name, [])
        return sorted(metrics, key=lambda m: m.timestamp, reverse=True)[:limit]

    async def subscribe_to_events(self, handler) -> None:
        """Subscribe handler (an EventSink with async handle) to all events."""
        self._event_bus.subscribe(handler)

    async def publish_event(self, event: ControlEvent) -> None:
        """Publish a control event."""
        await self._event_bus.publish(event)
        # Also log the event
        entry = LogEntry(
            grow_id=event.grow_id,
            level=event.severity,
            component=event.event_type.value,
            message=event.message,
            metadata={"stage": event.stage_name, "metric": event.metric},
        )
        await self.log(entry)
