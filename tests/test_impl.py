"""Tests for observability implementation."""

import pytest

from pyfarm.observability import (
    HealthStatus,
    LogEntry,
    Metric,
    ObservabilityImpl,
)


@pytest.mark.asyncio
async def test_log_write_and_query():
    obs = ObservabilityImpl()

    # Write logs
    await obs.log(LogEntry(grow_id="grow-1", level="info", component="control"))
    await obs.log(LogEntry(grow_id="grow-1", level="warning", component="sensor"))

    # Query all logs
    logs = await obs.query_logs("grow-1")
    assert len(logs) == 2

    # Query by component
    logs = await obs.query_logs("grow-1", component="control")
    assert len(logs) == 1
    assert logs[0].component == "control"

    # Query by level
    logs = await obs.query_logs("grow-1", level="warning")
    assert len(logs) == 1
    assert logs[0].level == "warning"


@pytest.mark.asyncio
async def test_metric_recording():
    obs = ObservabilityImpl()

    # Record metrics
    await obs.record_metric(Metric(name="temperature", value=22.5, unit="C"))
    await obs.record_metric(Metric(name="temperature", value=22.3, unit="C"))
    await obs.record_metric(Metric(name="humidity", value=65.0, unit="%"))

    # Query metrics
    temps = await obs.query_metrics("temperature")
    assert len(temps) == 2

    humidity = await obs.query_metrics("humidity")
    assert len(humidity) == 1

    nonexistent = await obs.query_metrics("nonexistent")
    assert len(nonexistent) == 0


@pytest.mark.asyncio
async def test_health_check():
    obs = ObservabilityImpl()

    # Initial check should be healthy
    health = await obs.check_health("sensor-1")
    assert health.status == HealthStatus.HEALTHY

    # Record a reading
    await obs._health_monitor.record_reading("sensor-1")
    health = await obs.check_health("sensor-1")
    assert health.status == HealthStatus.HEALTHY

    # Record multiple errors
    for _ in range(10):
        await obs._health_monitor.record_reading("sensor-1", error="Read failed")

    health = await obs.check_health("sensor-1")
    assert health.status == HealthStatus.UNHEALTHY
    assert health.metrics.get("error_count") == 10


@pytest.mark.asyncio
async def test_multiple_grows():
    obs = ObservabilityImpl()

    # Log to multiple grows
    await obs.log(LogEntry(grow_id="grow-1", message="Start grow 1"))
    await obs.log(LogEntry(grow_id="grow-2", message="Start grow 2"))

    logs1 = await obs.query_logs("grow-1")
    logs2 = await obs.query_logs("grow-2")

    assert len(logs1) == 1
    assert len(logs2) == 1
    assert logs1[0].grow_id == "grow-1"
    assert logs2[0].grow_id == "grow-2"


@pytest.mark.asyncio
async def test_log_limit():
    obs = ObservabilityImpl()

    # Write more than limit
    for i in range(150):
        await obs.log(LogEntry(grow_id="grow-1", message=f"Log {i}"))

    # Query with limit
    logs = await obs.query_logs("grow-1", limit=50)
    assert len(logs) == 50
