from collections.abc import Generator
from contextlib import contextmanager

from emilounge.api.routes.prerecordings import errors as e
from emilounge.api.routes.prerecordings import models as m
from emilounge.services.prerecordings import errors as pe
from emilounge.services.prerecordings import models as pm
from emilounge.services.prerecordings.service import PrerecordingsService


class Service:
    """Service for the prerecordings endpoint."""

    def __init__(self, prerecordings: PrerecordingsService):
        self._prerecordings = prerecordings

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except pe.EventNotFoundError as ex:
            raise e.EventNotFoundError(str(ex)) from ex
        except pe.BadEventTypeError as ex:
            raise e.BadEventTypeError(str(ex)) from ex
        except pe.InstanceNotFoundError as ex:
            raise e.InstanceNotFoundError(str(ex)) from ex
        except pe.PrerecordingNotFoundError as ex:
            raise e.PrerecordingNotFoundError(str(ex)) from ex
        except pe.EmishowsError as ex:
            raise e.EmishowsError(str(ex)) from ex
        except pe.MedialoungeError as ex:
            raise e.MedialoungeError(str(ex)) from ex
        except pe.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List prerecordings."""

        event = request.event
        after = request.after
        before = request.before
        limit = request.limit
        offset = request.offset
        order = request.order

        req = pm.ListRequest(
            event=event,
            after=after,
            before=before,
            limit=limit,
            offset=offset,
            order=order,
        )

        with self._handle_errors():
            res = await self._prerecordings.list(req)

        count = res.count
        prerecordings = res.prerecordings

        prerecordings = [
            m.Prerecording.map(prerecording) for prerecording in prerecordings
        ]
        results = m.PrerecordingList(
            count=count,
            limit=limit,
            offset=offset,
            prerecordings=prerecordings,
        )
        return m.ListResponse(
            results=results,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a prerecording."""

        event = request.event
        start = request.start

        req = pm.DownloadRequest(
            event=event,
            start=start,
        )

        with self._handle_errors():
            res = await self._prerecordings.download(req)

        content = res.content

        type = content.type
        size = content.size
        tag = content.tag
        modified = content.modified
        data = content.data
        return m.DownloadResponse(
            type=type,
            size=size,
            tag=tag,
            modified=modified,
            data=data,
        )

    async def headdownload(
        self, request: m.HeadDownloadRequest
    ) -> m.HeadDownloadResponse:
        """Download prerecording headers."""

        event = request.event
        start = request.start

        req = pm.DownloadRequest(
            event=event,
            start=start,
        )

        with self._handle_errors():
            res = await self._prerecordings.download(req)

        content = res.content

        type = content.type
        size = content.size
        tag = content.tag
        modified = content.modified
        return m.HeadDownloadResponse(
            type=type,
            size=size,
            tag=tag,
            modified=modified,
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a prerecording."""

        event = request.event
        start = request.start
        type = request.type
        data = request.data

        content = pm.UploadContent(
            type=type,
            data=data,
        )
        req = pm.UploadRequest(
            event=event,
            start=start,
            content=content,
        )

        with self._handle_errors():
            await self._prerecordings.upload(req)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a prerecording."""

        event = request.event
        start = request.start

        req = pm.DeleteRequest(
            event=event,
            start=start,
        )

        with self._handle_errors():
            await self._prerecordings.delete(req)

        return m.DeleteResponse()
