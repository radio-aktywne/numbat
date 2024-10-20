from collections.abc import Generator
from contextlib import contextmanager

from numbat.api.routes.ping import errors as e
from numbat.api.routes.ping import models as m
from numbat.services.ping import errors as pe
from numbat.services.ping import models as pm
from numbat.services.ping.service import PingService


class Service:
    """Service for the ping endpoint."""

    def __init__(self, ping: PingService) -> None:
        self._ping = ping

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except pe.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def ping(self, request: m.PingRequest) -> m.PingResponse:
        """Ping."""

        req = pm.PingRequest()

        with self._handle_errors():
            await self._ping.ping(req)

        return m.PingResponse()

    async def headping(self, request: m.HeadPingRequest) -> m.HeadPingResponse:
        """Ping headers."""

        return m.HeadPingResponse()
