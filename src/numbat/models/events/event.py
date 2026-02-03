from typing import Annotated

from pydantic import Field

from numbat.models.events import bar as be
from numbat.models.events import foo as fe

type Event = Annotated[be.BarEvent | fe.FooEvent, Field(discriminator="type")]
