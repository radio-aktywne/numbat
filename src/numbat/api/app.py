from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from numbat.api.lifespans import SuppressHTTPXLoggingLifespan, TestLifespan
from numbat.api.openapi import OpenAPIConfigBuilder
from numbat.api.plugins.pydantic import PydanticPlugin
from numbat.api.routes.router import router
from numbat.config.models import Config
from numbat.services.amber.service import AmberService
from numbat.services.beaver.service import BeaverService
from numbat.state import State


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.

    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_lifespan(
        self,
    ) -> Sequence[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            TestLifespan,
            SuppressHTTPXLoggingLifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfigBuilder().build()

    def _build_plugins(self) -> Sequence[PluginProtocol]:
        return [
            ChannelsPlugin(backend=MemoryChannelsBackend(), channels=["events"]),
            PydanticPlugin(),
        ]

    def _build_initial_state(self) -> State:
        return State(
            {
                "config": self._config,
                "amber": AmberService(config=self._config.amber),
                "beaver": BeaverService(config=self._config.beaver),
            }
        )

    def build(self) -> Litestar:
        """Build the app."""
        return Litestar(
            route_handlers=[router],
            debug=self._config.debug,
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
