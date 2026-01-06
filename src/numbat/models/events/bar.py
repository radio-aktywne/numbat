from typing import Literal

from pydantic import Field

from numbat.models.base import SerializableModel
from numbat.models.events import types as t
from numbat.utils.time import naiveutcnow


class BarEventData(SerializableModel):
    """Data of a bar event."""

    bar: str
    """Bar field."""


class BarEvent(SerializableModel):
    """Bar event."""

    type: t.TypeField[Literal["bar"]] = "bar"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[BarEventData]
