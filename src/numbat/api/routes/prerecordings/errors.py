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


class AmberError(ServiceError):
    """Raised when a amber database error occurs."""

    pass


class BeaverError(ServiceError):
    """Raised when an beaver service error occurs."""

    pass
