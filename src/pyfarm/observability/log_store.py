"""Time-series log storage."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Optional

from pyfarm.observability.models import LogEntry


class LogStore:
    """In-memory time-series log storage with TTL."""

    def __init__(self, max_entries_per_grow: int = 10000, ttl_hours: int = 168):
        """Initialize log store.

        Args:
            max_entries_per_grow: Maximum log entries per grow_id
            ttl_hours: Time-to-live for log entries (hours)
        """
        self.max_entries = max_entries_per_grow
        self.ttl = timedelta(hours=ttl_hours)
        self._logs: dict[str, deque[LogEntry]] = defaultdict(
            lambda: deque(maxlen=max_entries_per_grow)
        )

    async def write(self, entry: LogEntry) -> None:
        """Write a log entry."""
        self._logs[entry.grow_id].append(entry)

    async def query(
        self,
        grow_id: str,
        component: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Query logs for a grow.

        Args:
            grow_id: Grow ID to query
            component: Filter by component (e.g. "control", "sensor")
            level: Filter by level (e.g. "info", "warning")
            limit: Maximum entries to return

        Returns:
            List of log entries matching criteria
        """
        logs = list(self._logs.get(grow_id, []))
        now = datetime.now(timezone.utc)

        # Filter by timestamp (TTL)
        logs = [log for log in logs if now - log.timestamp < self.ttl]

        # Filter by component
        if component:
            logs = [log for log in logs if log.component == component]

        # Filter by level
        if level:
            logs = [log for log in logs if log.level == level]

        # Return most recent, limited
        return sorted(logs, key=lambda l: l.timestamp, reverse=True)[:limit]

    async def clear(self, grow_id: str) -> None:
        """Clear all logs for a grow."""
        if grow_id in self._logs:
            self._logs[grow_id].clear()
