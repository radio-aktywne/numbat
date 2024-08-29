import builtins
from collections.abc import Generator
from contextlib import contextmanager

from pydantic import TypeAdapter, ValidationError

from emilounge.services.emishows import errors as e


class Serializer[T]:
    """Serializes data."""

    def __init__(self, type: builtins.type[T]) -> None:
        self.Adapter = TypeAdapter(type)

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ValidationError as ex:
            raise e.ServiceError(ex.errors(include_context=False)) from ex

    def json(self, value: T) -> str:
        """Serialize to JSON."""

        with self._handle_errors():
            json = self.Adapter.dump_json(value, by_alias=True)

        json = json.decode()

        if json.startswith('"') and json.endswith('"'):
            json = json[1:-1]

        return json
