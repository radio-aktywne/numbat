from collections.abc import AsyncGenerator, AsyncIterator
from datetime import datetime

from numbat.models.base import datamodel


@datamodel
class ObjectListing:
    """Object listing model."""

    name: str
    """Name of the object."""


@datamodel
class ObjectDetails:
    """Object details model."""

    name: str
    """Name of the object."""

    type: str
    """Content type of the object."""

    size: int
    """Size of the object in bytes."""

    tag: str
    """ETag of the object."""

    modified: datetime
    """Datetime when the object was last modified."""


@datamodel
class UploadContent:
    """Content model for upload."""

    type: str
    """Content type of the object."""

    data: AsyncIterator[bytes]
    """Asynchronous iterator of data bytes."""


@datamodel
class DownloadContent:
    """Content model for download."""

    type: str
    """Content type of the object."""

    size: int
    """Size of the object in bytes."""

    tag: str
    """ETag of the object."""

    modified: datetime
    """Datetime when the object was last modified."""

    data: AsyncGenerator[bytes]
    """Asynchronous generator of data bytes."""


@datamodel
class ListRequest:
    """Request for listing objects."""

    prefix: str | None = None
    """Prefix of the object names."""

    recursive: bool = True
    """Whether to list objects recursively."""


@datamodel
class ListResponse:
    """Response for listing objects."""

    objects: AsyncGenerator[ObjectListing]
    """Asynchronous generator of object listings."""


@datamodel
class GetRequest:
    """Request for getting an object."""

    name: str
    """Name of the object."""


@datamodel
class GetResponse:
    """Response for getting an object."""

    object: ObjectDetails
    """Requested object details."""


@datamodel
class DownloadRequest:
    """Request for downloading object's data."""

    name: str
    """Name of the object."""

    chunk: int = 5 * (1024**2)
    """Chunk size for downloading."""


@datamodel
class DownloadResponse:
    """Response for downloading object's data."""

    content: DownloadContent
    """Downloaded content."""


@datamodel
class UploadRequest:
    """Request for uploading an object."""

    name: str
    """Name of the object."""

    content: UploadContent
    """Content of the object."""

    chunk: int = 5 * (1024**2)
    """Chunk size for uploading."""


@datamodel
class UploadResponse:
    """Response for uploading an object."""


@datamodel
class CopyRequest:
    """Request for copying an object."""

    source: str
    """Name of the source object."""

    destination: str
    """Name of the destination object."""


@datamodel
class CopyResponse:
    """Response for copying an object."""


@datamodel
class DeleteRequest:
    """Request for deleting an object."""

    name: str
    """Name of the object."""


@datamodel
class DeleteResponse:
    """Response for deleting an object."""
