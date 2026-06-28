import asyncio
from collections.abc import Callable, Generator, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import datetime
from enum import StrEnum
from typing import Any, BinaryIO, Never, cast, override

from minio import Minio
from minio.commonconfig import CopySource
from minio.datatypes import Object
from minio.error import MinioException, S3Error
from urllib3 import BaseHTTPResponse

from numbat.config.models import AmberConfig
from numbat.services.data.amber import errors as e
from numbat.services.data.amber import models as m
from numbat.utils import asyncify, syncify
from numbat.utils.read import ReadableIterator
from numbat.utils.time import httpparse


class ErrorCodes(StrEnum):
    """Error codes."""

    NOT_FOUND = "NoSuchKey"


class AmberService:
    """Service for amber database."""

    def __init__(self, config: AmberConfig) -> None:
        self._client = Minio(
            endpoint=config.s3.endpoint,
            access_key=config.s3.user,
            secret_key=config.s3.password,
            secure=config.s3.secure,
            cert_check=False,
        )
        self._bucket = config.s3.bucket

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except MinioException as ex:
            raise e.ServiceError from ex

    @contextmanager
    def _handle_not_found(self, name: str) -> Generator[None]:
        try:
            yield
        except S3Error as ex:
            if ex.code == ErrorCodes.NOT_FOUND:
                raise e.NotFoundError(name) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List objects."""

        def iterate(objects: Iterator[Object]) -> Generator[m.ObjectListing]:
            with self._handle_errors():
                for obj in objects:
                    yield m.ObjectListing(name=str(obj.object_name))

        with self._handle_errors():
            objects = await asyncio.to_thread(
                self._client.list_objects,
                bucket_name=self._bucket,
                prefix=request.prefix,
                recursive=request.recursive,
            )

        return m.ListResponse(objects=asyncify.Generator(iterate(objects)))

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get an object."""
        with self._handle_errors(), self._handle_not_found(request.name):
            obj = await asyncio.to_thread(
                self._client.stat_object,
                bucket_name=self._bucket,
                object_name=request.name,
            )

        return m.GetResponse(
            object=m.ObjectDetails(
                name=str(obj.object_name),
                type=str(obj.content_type),
                size=int(obj.size or 0),
                tag=str(obj.etag),
                modified=obj.last_modified or datetime.min,
            )
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download an object."""

        class Stream(Generator[bytes]):
            def __init__(
                self,
                response: BaseHTTPResponse,
                chunk: int,
                context: Callable[[], AbstractContextManager],
            ) -> None:
                self.response = response
                self.iterator = response.stream(chunk)
                self.context = context

            @override
            def send(self, *args: Any, **kwargs: Any) -> bytes:
                try:
                    with self.context():
                        return next(self.iterator)
                except:
                    self.response.close()
                    self.response.release_conn()
                    raise

            @override
            def throw(self, *args: Any, **kwargs: Any) -> Never:
                self.response.close()
                self.response.release_conn()
                raise StopIteration

        with self._handle_errors(), self._handle_not_found(request.name):
            get_object_response = await asyncio.to_thread(
                self._client.get_object,
                bucket_name=self._bucket,
                object_name=request.name,
            )

        return m.DownloadResponse(
            content=m.DownloadContent(
                type=get_object_response.headers["Content-Type"],
                size=int(get_object_response.headers["Content-Length"]),
                tag=get_object_response.headers["ETag"],
                modified=httpparse(get_object_response.headers["Last-Modified"]),
                data=asyncify.Generator(
                    Stream(get_object_response, request.chunk, self._handle_errors)
                ),
            )
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload an object."""
        with self._handle_errors():
            await asyncio.to_thread(
                self._client.put_object,
                bucket_name=self._bucket,
                object_name=request.name,
                data=cast(
                    "BinaryIO", ReadableIterator(syncify.Iterator(request.content.data))
                ),
                length=-1,
                content_type=request.content.type,
                part_size=request.chunk,
            )

        return m.UploadResponse()

    async def copy(self, request: m.CopyRequest) -> m.CopyResponse:
        """Copy an object."""
        with self._handle_errors(), self._handle_not_found(request.source):
            await asyncio.to_thread(
                self._client.copy_object,
                bucket_name=self._bucket,
                object_name=request.destination,
                source=CopySource(bucket_name=self._bucket, object_name=request.source),
            )

        return m.CopyResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete an object."""
        with self._handle_errors(), self._handle_not_found(request.name):
            await asyncio.to_thread(
                self._client.remove_object,
                bucket_name=self._bucket,
                object_name=request.name,
            )

        return m.DeleteResponse()
