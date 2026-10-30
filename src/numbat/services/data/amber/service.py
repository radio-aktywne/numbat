from collections.abc import AsyncGenerator, AsyncIterator, Generator
from contextlib import contextmanager

from obstore.exceptions import BaseError as ObstoreError
from obstore.store import S3Store

from numbat.config.models import AmberConfig
from numbat.services.data.amber import errors as e, models as m


class AmberService:
    """Service for amber database."""

    def __init__(self, config: AmberConfig) -> None:
        self._client = S3Store(
            bucket=config.s3.bucket,
            endpoint=config.s3.url,
            access_key_id=config.s3.user,
            secret_access_key=config.s3.password,
            client_options={
                "allow_http": not config.s3.secure,
                "allow_invalid_certificates": True,
                "read_timeout": "60s",
                "timeout": "24h",
            },
        )

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except (ObstoreError, OSError, NotImplementedError) as ex:
            raise e.ServiceError from ex

    @contextmanager
    def _handle_not_found(self, name: str) -> Generator[None]:
        try:
            yield
        except FileNotFoundError as ex:
            raise e.NotFoundError(name) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List objects."""

        async def iterate() -> AsyncGenerator[m.ObjectListing]:
            with self._handle_errors():
                if request.recursive:
                    async for batch in self._client.list(prefix=request.prefix):
                        for obj in batch:
                            yield m.ObjectListing(name=obj["path"])
                else:
                    result = await self._client.list_with_delimiter_async(
                        prefix=request.prefix
                    )
                    for obj in result["objects"]:
                        yield m.ObjectListing(name=obj["path"])

        return m.ListResponse(objects=iterate())

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get an object."""
        with self._handle_errors(), self._handle_not_found(request.name):
            response = await self._client.get_async(
                request.name, options={"head": True}
            )

        metadata = response.meta
        attributes = response.attributes

        if (tag := metadata["e_tag"]) is None:
            raise e.ServiceError("Object metadata is missing an ETag.")

        return m.GetResponse(
            object=m.ObjectDetails(
                name=metadata["path"],
                type=attributes["Content-Type"],
                size=metadata["size"],
                tag=tag,
                modified=metadata["last_modified"],
            )
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download an object."""

        async def iterate(stream: AsyncIterator[bytes]) -> AsyncGenerator[bytes]:
            with self._handle_errors():
                async for chunk in stream:
                    yield chunk

        with self._handle_errors(), self._handle_not_found(request.name):
            response = await self._client.get_async(request.name)

        metadata = response.meta
        attributes = response.attributes

        if (tag := metadata["e_tag"]) is None:
            raise e.ServiceError("Object metadata is missing an ETag.")

        return m.DownloadResponse(
            content=m.DownloadContent(
                type=attributes["Content-Type"],
                size=metadata["size"],
                tag=tag,
                modified=metadata["last_modified"],
                data=iterate(response.stream(min_chunk_size=request.chunk)),
            )
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload an object."""
        with self._handle_errors():
            await self._client.put_async(
                request.name,
                request.content.data,
                attributes={"Content-Type": request.content.type},
                chunk_size=request.chunk,
            )

        return m.UploadResponse()

    async def copy(self, request: m.CopyRequest) -> m.CopyResponse:
        """Copy an object."""
        with self._handle_errors(), self._handle_not_found(request.source):
            await self._client.copy_async(request.source, request.destination)

        return m.CopyResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete an object."""
        with self._handle_errors(), self._handle_not_found(request.name):
            await self._client.delete_async(request.name)

        return m.DeleteResponse()
