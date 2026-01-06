from typing import override

from gracy.exceptions import REDUCE_PICKABLE_RETURN
from gracy.exceptions import GracyException as ServiceError


class SerializationError(ServiceError):
    """Error during serialization."""

    @override
    def __reduce__(self) -> REDUCE_PICKABLE_RETURN:
        return (SerializationError, self.args)
