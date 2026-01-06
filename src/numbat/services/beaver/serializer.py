from typing import Any, Self

from pydantic import (
    ModelWrapValidatorHandler,
    RootModel,
    ValidationError,
    model_validator,
)
from pydantic_core import PydanticSerializationError

from numbat.services.beaver import errors as e


class Serializer[T](RootModel[T]):
    """Serializes data."""

    @model_validator(mode="wrap")
    @classmethod
    def validator(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        """Validate input data."""
        try:
            return handler(data)
        except ValidationError as ex:
            raise e.SerializationError(ex.errors(include_context=False)) from ex

    @classmethod
    def serialize(cls, value: T) -> str:
        """Serialize the value."""
        try:
            return cls.model_validate(value).model_dump_json(by_alias=True).strip('"')
        except PydanticSerializationError as ex:
            raise e.SerializationError(str(ex)) from ex
