"""Event bus and subscription mechanism for pyfarm."""

from __future__ import annotations

from typing import Protocol

from pyfarm.core.models import ControlEvent


class EventSubscriber(Protocol):
    """Protocol for event subscribers."""

    async def handle_event(self, event: ControlEvent) -> None:
        """Handle an event."""
        ...


class EventSink(Protocol):
    """Protocol for event sinks (handlers that process events)."""

    async def handle(self, event: ControlEvent) -> None:
        """Handle an event."""
        ...


class EventBus:
    """In-memory event bus for publishing and subscribing."""

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: dict[str, list[EventSubscriber]] = {}
        self._all_subscribers: list[EventSubscriber] = []

    async def subscribe(self, event_type: str, handler: EventSubscriber) -> None:
        """Subscribe to events of a given type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def subscribe_all(self, handler: EventSubscriber) -> None:
        """Subscribe to all events."""
        self._all_subscribers.append(handler)

    async def publish(self, event: ControlEvent) -> None:
        """Publish an event to all subscribers."""
        event_type = event.kind.value
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                await handler.handle_event(event)
        for handler in self._all_subscribers:
            await handler.handle_event(event)

    async def emit(self, event: ControlEvent) -> None:
        """Emit an event (alias for publish for compatibility)."""
        await self.publish(event)

    async def drain(self) -> None:
        """Drain/flush all pending events (no-op for in-memory bus)."""
        pass
