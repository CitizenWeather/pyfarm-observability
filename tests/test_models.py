"""Tests for observability models."""

from pyfarm.observability.models import HealthCheck, HealthStatus, LogEntry, Metric


def test_health_check_creation():
    check = HealthCheck(component="sensor", status=HealthStatus.HEALTHY)
    assert check.component == "sensor"
    assert check.status == HealthStatus.HEALTHY


def test_log_entry_creation():
    entry = LogEntry(grow_id="grow-1", level="info", component="control")
    assert entry.grow_id == "grow-1"
    assert entry.level == "info"
    assert entry.component == "control"


def test_metric_creation():
    metric = Metric(name="temperature", value=22.5, unit="C")
    assert metric.name == "temperature"
    assert metric.value == 22.5
    assert metric.unit == "C"
