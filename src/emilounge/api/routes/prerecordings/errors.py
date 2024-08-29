class ServiceError(Exception):
    """Base class for service errors."""

    pass


class BadEventTypeError(ServiceError):
    """Raised when event type is not supported."""

    pass


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    pass


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""

    pass


class PrerecordingNotFoundError(ServiceError):
    """Raised when prerecording is not found."""

    pass


class EmishowsError(ServiceError):
    """Raised when an emishows service error occurs."""

    pass


class MedialoungeError(ServiceError):
    """Raised when a medialounge database error occurs."""

    pass
