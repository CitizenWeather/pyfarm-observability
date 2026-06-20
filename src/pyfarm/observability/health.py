"""Health check evaluation and monitoring."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from pyfarm.observability.models import HealthCheck, HealthStatus


class HealthMonitor:
    """Monitors health of system components."""

    def __init__(self, stale_data_threshold_seconds: int = 60):
        """Initialize health monitor.

        Args:
            stale_data_threshold_seconds: Consider data stale if older than this
        """
        self.stale_threshold = timedelta(seconds=stale_data_threshold_seconds)
        self._last_reading: dict[str, datetime] = {}
        self._error_counts: dict[str, int] = {}

    async def record_reading(self, sensor_id: str, error: Optional[str] = None) -> None:
        """Record a sensor reading.

        Args:
            sensor_id: ID of sensor that produced reading
            error: Error message if read failed, None if successful
        """
        self._last_reading[sensor_id] = datetime.now(timezone.utc)
        if error:
            self._error_counts[sensor_id] = self._error_counts.get(sensor_id, 0) + 1
        else:
            self._error_counts[sensor_id] = 0

    async def check_health(self, component: str) -> HealthCheck:
        """Check health of a component.

        Args:
            component: Component name (e.g. "sensor-temp-1", "control-loop")

        Returns:
            Health check result
        """
        now = datetime.now(timezone.utc)
        status = HealthStatus.HEALTHY
        message = "OK"
        metrics = {}

        # Check if data is stale
        last_reading = self._last_reading.get(component)
        if last_reading and (now - last_reading) > self.stale_threshold:
            status = HealthStatus.DEGRADED
            message = f"No reading for {(now - last_reading).seconds}s"
            metrics["staleness_seconds"] = (now - last_reading).seconds

        # Check error count
        error_count = self._error_counts.get(component, 0)
        if error_count > 5:
            status = HealthStatus.UNHEALTHY
            message = f"{error_count} consecutive errors"
            metrics["error_count"] = error_count

        return HealthCheck(
            component=component,
            status=status,
            message=message,
            metrics=metrics,
        )

    async def reset_errors(self, component: str) -> None:
        """Reset error counter for a component."""
        self._error_counts[component] = 0
