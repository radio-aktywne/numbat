from collections.abc import Sequence

from pydantic import BaseModel, Field

from numbat.config.base import BaseConfig


class AmberS3Config(BaseModel):
    """Configuration for the S3 API of the amber database."""

    host: str = "localhost"
    """Host of the S3 API."""

    password: str = "password"  # noqa: S105
    """Password to authenticate with the S3 API."""

    port: int | None = Field(default=10610, ge=1, le=65535)
    """Port of the S3 API."""

    secure: bool = False
    """Whether to use a secure connection."""

    user: str = "readwrite"
    """Username to authenticate with the S3 API."""

    @property
    def bucket(self) -> str:
        """Bucket to store media in."""
        return "default"

    @property
    def endpoint(self) -> str:
        """Endpoint to connect to the S3 API."""
        if self.port is None:
            return self.host

        return f"{self.host}:{self.port}"


class AmberConfig(BaseModel):
    """Configuration for the amber database."""

    s3: AmberS3Config = AmberS3Config()
    """Configuration for the S3 API of the amber database."""


class BeaverHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the beaver service."""

    host: str = "localhost"
    """Host of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    port: int | None = Field(default=10500, ge=1, le=65535)
    """Port of the HTTP API."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class BeaverConfig(BaseModel):
    """Configuration for the beaver service."""

    http: BeaverHTTPConfig = BeaverHTTPConfig()
    """Configuration for the HTTP API of the beaver service."""


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    port: int = Field(default=10600, ge=0, le=65535)
    """Port to run the server on."""

    trusted: str | Sequence[str] | None = "*"
    """Trusted IP addresses."""


class Config(BaseConfig):
    """Configuration for the service."""

    amber: AmberConfig = AmberConfig()
    """Configuration for the amber database."""

    beaver: BeaverConfig = BeaverConfig()
    """Configuration for the beaver service."""

    debug: bool = True
    """Enable debug mode."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""
