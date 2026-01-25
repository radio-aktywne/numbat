from collections.abc import AsyncIterator, Sequence
from datetime import datetime
from uuid import UUID

from numbat.models.base import SerializableModel, datamodel
from numbat.services.prerecordings import models as pm
from numbat.utils.time import NaiveDatetime


class Prerecording(SerializableModel):
    """Prerecording data."""

    event: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""

    @staticmethod
    def map(prerecording: pm.Prerecording) -> "Prerecording":
        """Map to internal representation."""
        return Prerecording(
            event=prerecording.event,
            start=prerecording.start,
        )


class PrerecordingList(SerializableModel):
    """List of prerecordings."""

    count: int
    """Total number of prerecordings that match the request."""

    limit: int | None
    """Maximum number of returned prerecordings."""

    offset: int | None
    """Number of skipped prerecordings."""

    prerecordings: Sequence[Prerecording]
    """List of prerecordings."""


ListRequestEvent = UUID

ListRequestAfter = NaiveDatetime | None

ListRequestBefore = NaiveDatetime | None

ListRequestLimit = int | None

ListRequestOffset = int | None

ListRequestOrder = pm.ListOrder | None

ListResponseResults = PrerecordingList

DownloadRequestEvent = UUID

DownloadRequestStart = NaiveDatetime

DownloadResponseType = str

DownloadResponseSize = int

DownloadResponseTag = str

DownloadResponseModified = datetime

DownloadResponseData = AsyncIterator[bytes]

HeadDownloadRequestEvent = UUID

HeadDownloadRequestStart = NaiveDatetime

HeadDownloadResponseType = str

HeadDownloadResponseSize = int

HeadDownloadResponseTag = str

HeadDownloadResponseModified = datetime

UploadRequestEvent = UUID

UploadRequestStart = NaiveDatetime

UploadRequestType = str

UploadRequestData = AsyncIterator[bytes]

DeleteRequestEvent = UUID

DeleteRequestStart = NaiveDatetime


@datamodel
class ListRequest:
    """Request to list prerecordings."""

    event: ListRequestEvent
    """Identifier of the event to list prerecordings for."""

    after: ListRequestAfter
    """Only list prerecordings after this time (in event timezone)."""

    before: ListRequestBefore
    """Only list prerecordings before this date (in event timezone)."""

    limit: ListRequestLimit
    """Maximum number of prerecordings to return."""

    offset: ListRequestOffset
    """Number of prerecordings to skip."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing prerecordings."""

    results: ListResponseResults
    """List of prerecordings."""


@datamodel
class DownloadRequest:
    """Request to download a prerecording."""

    event: DownloadRequestEvent
    """Identifier of the event."""

    start: DownloadRequestStart
    """Start time of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a prerecording."""

    type: DownloadResponseType
    """Type of the prerecording data."""

    size: DownloadResponseSize
    """Size of the prerecording in bytes."""

    tag: DownloadResponseTag
    """ETag of the prerecording data."""

    modified: DownloadResponseModified
    """Date and time when the prerecording was last modified."""

    data: DownloadResponseData
    """Data of the prerecording."""


@datamodel
class HeadDownloadRequest:
    """Request to download prerecording headers."""

    event: HeadDownloadRequestEvent
    """Identifier of the event."""

    start: HeadDownloadRequestStart
    """Start time of the event instance in event timezone."""


@datamodel
class HeadDownloadResponse:
    """Response for downloading prerecording headers."""

    type: HeadDownloadResponseType
    """Type of the prerecording data."""

    size: HeadDownloadResponseSize
    """Size of the prerecording in bytes."""

    tag: HeadDownloadResponseTag
    """ETag of the prerecording data."""

    modified: HeadDownloadResponseModified
    """Date and time when the prerecording was last modified."""


@datamodel
class UploadRequest:
    """Request to upload a prerecording."""

    event: UploadRequestEvent
    """Identifier of the event."""

    start: UploadRequestStart
    """Start time of the event instance in event timezone."""

    type: UploadRequestType
    """Type of the prerecording data."""

    data: UploadRequestData
    """Data of the prerecording."""


@datamodel
class UploadResponse:
    """Response for uploading a prerecording."""


@datamodel
class DeleteRequest:
    """Request to delete a prerecording."""

    event: DeleteRequestEvent
    """Identifier of the event."""

    start: DeleteRequestStart
    """Start time of the event instance in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting a prerecording."""
