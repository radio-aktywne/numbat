from datetime import datetime
from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class BadEventTypeError(ServiceError):
    """Raised when event type is not supported."""

    def __init__(self, type: str) -> None:
        super().__init__(f"Event of type {type} cannot have a prerecording.")


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"Prerecorded event not found for id {event}.")


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"Instance not found for prerecorded event {event} starting at {start}."
        )


class PrerecordingNotFoundError(ServiceError):
    """Raised when prerecording is not found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"Prerecording not found for instance of prerecorded event {event} starting at {start}."
        )


class EmishowsError(ServiceError):
    """Raised when an emishows service operation fails."""

    pass


class MedialoungeError(ServiceError):
    """Raised when a medialounge database operation fails."""

    pass
