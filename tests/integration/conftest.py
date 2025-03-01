from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, BasicAuth
from litestar import Litestar
from litestar.testing import AsyncTestClient
from minio import Minio

from numbat.api.app import AppBuilder
from numbat.config.builder import ConfigBuilder
from numbat.config.models import Config
from tests.utils.containers import AsyncDockerContainer
from tests.utils.waiting.conditions import CallableCondition, CommandCondition
from tests.utils.waiting.strategies import TimeoutStrategy
from tests.utils.waiting.waiter import Waiter


@pytest.fixture(scope="session")
def config() -> Config:
    """Loaded configuration."""

    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Reusable application."""

    return AppBuilder(config).build()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def howlite() -> AsyncGenerator[AsyncDockerContainer]:
    """Howlite container."""

    async def _check() -> None:
        auth = BasicAuth(username="user", password="password")
        async with AsyncClient(base_url="http://localhost:10520", auth=auth) as client:
            response = await client.get("/user/calendar")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/howlite:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def sapphire() -> AsyncGenerator[AsyncDockerContainer]:
    """Sapphire container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/sapphire:latest",
        network="host",
        privileged=True,
    )

    waiter = Waiter(
        condition=CommandCondition(
            [
                "usql",
                "--command",
                "SELECT 1;",
                "postgres://user:password@localhost:10510/database",
            ]
        ),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def amber() -> AsyncGenerator[AsyncDockerContainer]:
    """Amber container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10610") as client:
            response = await client.get("/minio/health/ready")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/amber:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def beaver(
    howlite: AsyncDockerContainer, sapphire: AsyncDockerContainer
) -> AsyncGenerator[AsyncDockerContainer]:
    """Beaver container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10500") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/services/beaver:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest.fixture(scope="session")
def amber_client(amber: AsyncDockerContainer) -> Minio:
    """Amber client."""

    return Minio(
        endpoint="localhost:10610",
        access_key="readwrite",
        secret_key="password",
        secure=False,
        cert_check=False,
    )


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def beaver_client(
    beaver: AsyncDockerContainer,
) -> AsyncGenerator[AsyncClient]:
    """Beaver client."""

    async with AsyncClient(base_url="http://localhost:10500") as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def client(
    app: Litestar, amber: AsyncDockerContainer, beaver: AsyncDockerContainer
) -> AsyncGenerator[AsyncTestClient]:
    """Reusable test client."""

    async with AsyncTestClient(app=app) as client:
        yield client
