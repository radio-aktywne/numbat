class ServiceError(Exception):
    """Base class for service errors."""


class BadEventTypeError(ServiceError):
    """Raised when event type is not supported."""


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""


class PrerecordingNotFoundError(ServiceError):
    """Raised when prerecording is not found."""


class AmberError(ServiceError):
    """Raised when a amber database error occurs."""


class BeaverError(ServiceError):
    """Raised when an beaver service error occurs."""
