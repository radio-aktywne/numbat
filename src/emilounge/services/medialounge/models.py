from collections.abc import AsyncIterator
from datetime import datetime

from emilounge.models.base import datamodel


@datamodel
class Object:
    """Object model."""

    name: str
    """Name of the object."""

    modified: datetime | None
    """Date and time when the object was last modified."""

    size: int | None
    """Size of the object in bytes."""

    metadata: dict[str, str] | None
    """Metadata of the object."""

    type: str | None
    """Content type of the object."""


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
    """Date and time when the object was last modified."""

    data: AsyncIterator[bytes]
    """Asynchronous iterator of data bytes."""


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

    objects: AsyncIterator[Object]
    """Asynchronous iterator of objects."""


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

    object: Object
    """Uploaded object."""


@datamodel
class GetRequest:
    """Request for getting an object."""

    name: str
    """Name of the object."""


@datamodel
class GetResponse:
    """Response for getting an object."""

    object: Object
    """Requested object."""


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
class CopyRequest:
    """Request for copying an object."""

    source: str
    """Name of the source object."""

    destination: str
    """Name of the destination object."""


@datamodel
class CopyResponse:
    """Response for copying an object."""

    object: Object
    """Copied object."""


@datamodel
class DeleteRequest:
    """Request for deleting an object."""

    name: str
    """Name of the object."""


@datamodel
class DeleteResponse:
    """Response for deleting an object."""

    object: Object
    """Deleted object."""
