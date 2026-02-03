from collections.abc import Generator
from contextlib import contextmanager

from numbat.api.routes.prerecordings import errors as e
from numbat.api.routes.prerecordings import models as m
from numbat.services.prerecordings import errors as pe
from numbat.services.prerecordings import models as pm
from numbat.services.prerecordings.service import PrerecordingsService


class Service:
    """Service for the prerecordings endpoint."""

    def __init__(self, prerecordings: PrerecordingsService) -> None:
        self._prerecordings = prerecordings

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except pe.EventNotFoundError as ex:
            raise e.EventNotFoundError from ex
        except pe.BadEventTypeError as ex:
            raise e.BadEventTypeError from ex
        except pe.InstanceNotFoundError as ex:
            raise e.InstanceNotFoundError from ex
        except pe.PrerecordingNotFoundError as ex:
            raise e.PrerecordingNotFoundError from ex
        except pe.BeaverError as ex:
            raise e.BeaverError from ex
        except pe.AmberError as ex:
            raise e.AmberError from ex
        except pe.ServiceError as ex:
            raise e.ServiceError from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List prerecordings."""
        list_request = pm.ListRequest(
            event=request.event,
            after=request.after,
            before=request.before,
            limit=request.limit,
            offset=request.offset,
            order=request.order,
        )

        with self._handle_errors():
            list_response = await self._prerecordings.list(list_request)

        return m.ListResponse(
            results=m.PrerecordingList(
                count=list_response.count,
                limit=request.limit,
                offset=request.offset,
                prerecordings=[
                    m.Prerecording.map(prerecording)
                    for prerecording in list_response.prerecordings
                ],
            )
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a prerecording."""
        download_request = pm.DownloadRequest(event=request.event, start=request.start)

        with self._handle_errors():
            download_response = await self._prerecordings.download(download_request)

        return m.DownloadResponse(
            type=download_response.content.type,
            size=download_response.content.size,
            tag=download_response.content.tag,
            modified=download_response.content.modified,
            data=download_response.content.data,
        )

    async def headdownload(
        self, request: m.HeadDownloadRequest
    ) -> m.HeadDownloadResponse:
        """Download prerecording headers."""
        download_request = pm.DownloadRequest(event=request.event, start=request.start)

        with self._handle_errors():
            download_response = await self._prerecordings.download(download_request)

        return m.HeadDownloadResponse(
            type=download_response.content.type,
            size=download_response.content.size,
            tag=download_response.content.tag,
            modified=download_response.content.modified,
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a prerecording."""
        upload_request = pm.UploadRequest(
            event=request.event,
            start=request.start,
            content=pm.UploadContent(type=request.type, data=request.data),
        )

        with self._handle_errors():
            await self._prerecordings.upload(upload_request)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a prerecording."""
        delete_request = pm.DeleteRequest(event=request.event, start=request.start)

        with self._handle_errors():
            await self._prerecordings.delete(delete_request)

        return m.DeleteResponse()
