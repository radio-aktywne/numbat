from uuid import UUID

from numbat.utils.time import NaiveDatetime, isostringify


class ServiceError(Exception):
    """Base class for service errors."""


class BadEventTypeError(ServiceError):
    """Raised when event type is not supported."""

    def __init__(self, event_type: str) -> None:
        super().__init__(f"Event of type {event_type} cannot have a prerecording.")


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"Prerecorded event not found for id {event}.")


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""

    def __init__(self, event: UUID, start: NaiveDatetime) -> None:
        super().__init__(
            f"Instance not found for prerecorded event {event} starting at {isostringify(start)}."
        )


class PrerecordingNotFoundError(ServiceError):
    """Raised when prerecording is not found."""

    def __init__(self, event: UUID, start: NaiveDatetime) -> None:
        super().__init__(
            f"Prerecording not found for instance of prerecorded event {event} starting at {isostringify(start)}."
        )


class AmberError(ServiceError):
    """Raised when a amber database operation fails."""


class BeaverError(ServiceError):
    """Raised when an beaver service operation fails."""
