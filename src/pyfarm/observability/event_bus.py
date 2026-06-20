"""Event bus and subscription mechanism for pyfarm.

The bus is a *buffered event spine*: producers call :meth:`emit` synchronously
(cheap, non-blocking) during a control tick, and the consumer drains buffered
events to all registered sinks at a well-defined point via :meth:`drain`. This
keeps event production off the async path inside tight control loops while
still giving sinks an ``await``-friendly delivery point.
"""

from __future__ import annotations

from typing import Protocol

from pyfarm.core.models import ControlEvent


class EventSubscriber(Protocol):
    """Protocol for event subscribers (legacy alias of :class:`EventSink`)."""

    async def handle(self, event: ControlEvent) -> None:
        """Handle an event."""
        ...


class EventSink(Protocol):
    """Protocol for event sinks (handlers that process events)."""

    async def handle(self, event: ControlEvent) -> None:
        """Handle an event."""
        ...


class EventBus:
    """In-memory, buffered event bus.

    Usage::

        bus = EventBus()
        bus.subscribe(my_sink)      # sink implements async handle(event)
        bus.emit(event)             # synchronous, buffered
        await bus.drain()           # deliver buffered events to all sinks
    """

    def __init__(self) -> None:
        self._sinks: list[EventSink] = []
        self._buffer: list[ControlEvent] = []

    def subscribe(self, sink: EventSink) -> None:
        """Register a sink to receive events on :meth:`drain`."""
        self._sinks.append(sink)

    def emit(self, event: ControlEvent) -> None:
        """Buffer an event for later delivery. Synchronous and non-blocking."""
        self._buffer.append(event)

    async def drain(self) -> None:
        """Deliver all buffered events to every sink, then clear the buffer."""
        events = self._buffer
        self._buffer = []
        for event in events:
            for sink in self._sinks:
                await sink.handle(event)

    async def publish(self, event: ControlEvent) -> None:
        """Convenience: emit a single event and drain immediately."""
        self.emit(event)
        await self.drain()
