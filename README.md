# pyfarm-observability

Structured logging, metrics, and health checks for pyfarm.

## Purpose

System telemetry distinct from crop/yield analytics. This module answers "is the *software* healthy?" rather than "how is the crop growing?".

## Key Components

- **Structured Logging** — Control loop events (setpoint changes, sensor errors, actuator commands)
- **Health Checks** — Sensor drift detection, data staleness, actuator non-response
- **Metrics** — Loop iteration times, alert latency, persistence write latency
- **Tracing** — Correlate sensor spike → alert fired → actuator triggered
- **Watchdog** — Detects hung control loops, stale data streams

## Integration

- Subscribes to event bus (pyfarm-core)
- Writes to time-series store (pyfarm-storage)
- Queried by CLI (pyfarm-cli) for logs and status

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
