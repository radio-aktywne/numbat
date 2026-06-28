class ServiceError(Exception):
    """Base class for beaver service errors."""


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""
