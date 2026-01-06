from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from numbat.models.base import datamodel
from numbat.services.amber import models as am

DownloadContent = am.DownloadContent

UploadContent = am.UploadContent


class ListOrder(StrEnum):
    """Order to list prerecordings."""

    ASCENDING = "asc"
    DESCENDING = "desc"


@datamodel
class Prerecording:
    """Prerecording data."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""


@datamodel
class ListRequest:
    """Request to list prerecordings."""

    event: UUID
    """Identifier of the event to list prerecordings for."""

    after: datetime | None
    """Only list prerecordings after this time (in event timezone)."""

    before: datetime | None
    """Only list prerecordings before this date (in event timezone)."""

    limit: int | None
    """Maximum number of prerecordings to return."""

    offset: int | None
    """Number of prerecordings to skip."""

    order: ListOrder | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing prerecordings."""

    count: int
    """Total number of prerecordings that match the request."""

    limit: int | None
    """Maximum number of returned prerecordings."""

    offset: int | None
    """Number of skipped prerecordings."""

    prerecordings: Sequence[Prerecording]
    """List of prerecordings."""


@datamodel
class DownloadRequest:
    """Request to download a prerecording."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a prerecording."""

    content: DownloadContent
    """Content of the prerecording."""


@datamodel
class UploadRequest:
    """Request to upload a prerecording."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""

    content: UploadContent
    """Content of the prerecording."""


@datamodel
class UploadResponse:
    """Response for uploading a prerecording."""


@datamodel
class DeleteRequest:
    """Request to delete a prerecording."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting a prerecording."""
