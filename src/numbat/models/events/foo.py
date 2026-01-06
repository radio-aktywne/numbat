from typing import Literal

from pydantic import Field

from numbat.models.base import SerializableModel
from numbat.models.events import types as t
from numbat.utils.time import naiveutcnow


class FooEventData(SerializableModel):
    """Data of a foo event."""

    foo: str
    """Foo field."""


class FooEvent(SerializableModel):
    """Foo event."""

    type: t.TypeField[Literal["foo"]] = "foo"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[FooEventData]
