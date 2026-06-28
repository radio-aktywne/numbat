from datetime import datetime
from uuid import UUID

from numbat.utils.mime import MimeType
from numbat.utils.time import isostringify


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class BadEventTypeError(ValidationError):
    """Raised when event type is not supported."""

    def __init__(self, event_type: str) -> None:
        super().__init__(f"Event of type {event_type} cannot have a prerecording.")


class EventNotFoundError(ValidationError):
    """Raised when event is not found."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"Prerecorded event not found for id {event_id}.")


class InstanceNotFoundError(ValidationError):
    """Raised when instance is not found."""

    def __init__(self, event_id: UUID, start: datetime) -> None:
        super().__init__(
            f"Instance not found for prerecorded event {event_id} starting at {isostringify(start)}."
        )


class UnsupportedContentTypeError(ValidationError):
    """Raised when an unsupported content type is provided."""

    def __init__(self, content_type: MimeType) -> None:
        super().__init__(f"Unsupported content type: {content_type!s}.")


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""


class PrerecordingNotFoundError(NotFoundError):
    """Raised when prerecording is not found."""

    def __init__(self, event_id: UUID, start: datetime) -> None:
        super().__init__(
            f"Prerecording not found for instance of prerecorded event {event_id} starting at {isostringify(start)}."
        )
