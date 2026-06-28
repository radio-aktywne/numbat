class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class NotFoundError(ServiceError):
    """Raised when a prerecording is not found."""
