from pydantic import BaseModel, Field

from numbat.config.base import BaseConfig


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    port: int = Field(10600, ge=0, le=65535)
    """Port to run the server on."""

    trusted: str | list[str] | None = "*"
    """Trusted IP addresses."""


class AmberS3Config(BaseModel):
    """Configuration for the S3 API of the amber database."""

    secure: bool = False
    """Whether to use a secure connection."""

    host: str = "localhost"
    """Host of the S3 API."""

    port: int | None = Field(10610, ge=1, le=65535)
    """Port of the S3 API."""

    user: str = "readwrite"
    """Username to authenticate with the S3 API."""

    password: str = "password"
    """Password to authenticate with the S3 API."""

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

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(10500, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

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


class Config(BaseConfig):
    """Configuration for the service."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    amber: AmberConfig = AmberConfig()
    """Configuration for the amber database."""

    beaver: BeaverConfig = BeaverConfig()
    """Configuration for the beaver service."""

    debug: bool = False
    """Enable debug mode."""
