from collections.abc import AsyncGenerator
from typing import Annotated

from litestar import Controller as BaseController
from litestar import Request, handlers
from litestar.datastructures import ResponseHeader
from litestar.di import Provide
from litestar.exceptions import InternalServerException
from litestar.params import Parameter
from litestar.response import Response, Stream
from litestar.status_codes import HTTP_204_NO_CONTENT

from emilounge.api.exceptions import BadRequestException, NotFoundException
from emilounge.api.routes.prerecordings import errors as e
from emilounge.api.routes.prerecordings import models as m
from emilounge.api.routes.prerecordings.service import Service
from emilounge.api.validator import Validator
from emilounge.services.prerecordings.service import PrerecordingsService
from emilounge.state import State
from emilounge.utils.time import httpstringify


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            prerecordings=PrerecordingsService(
                emishows=state.emishows,
                medialounge=state.medialounge,
            )
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the prerecordings endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        "/{event:uuid}",
        summary="List prerecordings",
    )
    async def list(
        self,
        service: Service,
        event: Annotated[
            m.ListRequestEvent,
            Parameter(
                description="Identifier of the event to list prerecordings for.",
            ),
        ],
        after: Annotated[
            m.ListRequestAfter,
            Parameter(
                description="Only list prerecordings after this time (in event timezone).",
            ),
        ] = None,
        before: Annotated[
            m.ListRequestBefore,
            Parameter(
                description="Only list prerecordings before this time (in event timezone).",
            ),
        ] = None,
        limit: Annotated[
            m.ListRequestLimit,
            Parameter(
                description="Maximum number of prerecordings to return.",
            ),
        ] = 10,
        offset: Annotated[
            m.ListRequestOffset,
            Parameter(
                description="Number of prerecordings to skip.",
            ),
        ] = None,
        order: Annotated[
            m.ListRequestOrder,
            Parameter(
                description="Order to apply to the results.",
            ),
        ] = None,
    ) -> Response[m.ListResponseResults]:
        """List prerecordings."""

        req = m.ListRequest(
            event=event,
            after=after,
            before=before,
            limit=limit,
            offset=offset,
            order=order,
        )

        try:
            res = await service.list(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        results = res.results

        return Response(results)

    @handlers.get(
        "/{event:uuid}/{start:str}",
        summary="Download prerecording",
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                description="Content type.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                description="Content length.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                description="Entity tag.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                description="Last modified.",
                documentation_only=True,
            ),
        ],
    )
    async def download(
        self,
        service: Service,
        event: Annotated[
            m.DownloadRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            str,
            Parameter(
                description="Start time of the event instance in event timezone.",
            ),
        ],
    ) -> Stream:
        """Download a prerecording."""

        start = Validator(m.DownloadRequestStart).object(start)

        req = m.DownloadRequest(
            event=event,
            start=start,
        )

        try:
            res = await service.download(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex
        except e.PrerecordingNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        type = res.type
        size = res.size
        tag = res.tag
        modified = res.modified
        data = res.data

        headers = {
            "Content-Type": type,
            "Content-Length": str(size),
            "ETag": tag,
            "Last-Modified": httpstringify(modified),
        }
        return Stream(
            data,
            headers=headers,
        )

    @handlers.head(
        "/{event:uuid}/{start:str}",
        summary="Download prerecording headers",
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                description="Content type.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                description="Content length.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                description="Entity tag.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                description="Last modified.",
                documentation_only=True,
            ),
        ],
    )
    async def headdownload(
        self,
        service: Service,
        event: Annotated[
            m.HeadDownloadRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            str,
            Parameter(
                description="Start time of the event instance in event timezone.",
            ),
        ],
    ) -> Response[None]:
        """Download prerecording headers."""

        start = Validator(m.HeadDownloadRequestStart).object(start)

        req = m.HeadDownloadRequest(
            event=event,
            start=start,
        )

        try:
            res = await service.headdownload(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex
        except e.PrerecordingNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        type = res.type
        size = res.size
        tag = res.tag
        modified = res.modified

        headers = {
            "Content-Type": type,
            "Content-Length": str(size),
            "ETag": tag,
            "Last-Modified": httpstringify(modified),
        }
        return Response(
            None,
            headers=headers,
        )

    @handlers.put(
        "/{event:uuid}/{start:str}",
        summary="Upload prerecording",
        status_code=HTTP_204_NO_CONTENT,
    )
    async def upload(
        self,
        service: Service,
        event: Annotated[
            m.UploadRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            m.UploadRequestStart,
            Parameter(
                description="Start time of the event instance in event timezone.",
            ),
        ],
        type: Annotated[
            m.UploadRequestType,
            Parameter(
                header="Content-Type",
                description="Type of the prerecording data.",
            ),
        ],
        request: Request,
    ) -> Response[None]:
        """Upload a prerecording."""

        async def _stream(request: Request) -> AsyncGenerator[bytes]:
            stream = request.stream()
            while True:
                try:
                    chunk = await anext(stream)
                except (StopAsyncIteration, InternalServerException):
                    break

                yield chunk

        start = Validator(m.UploadRequestStart).object(start)

        req = m.UploadRequest(
            event=event,
            start=start,
            type=type,
            data=_stream(request),
        )

        try:
            await service.upload(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        return Response(None)

    @handlers.delete(
        "/{event:uuid}/{start:str}",
        summary="Delete prerecording",
    )
    async def delete(
        self,
        service: Service,
        event: Annotated[
            m.DeleteRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            str,
            Parameter(
                description="Start time of the event instance in event timezone.",
            ),
        ],
    ) -> Response[None]:
        """Delete a prerecording."""

        start = Validator(m.DeleteRequestStart).object(start)

        req = m.DeleteRequest(
            event=event,
            start=start,
        )

        try:
            await service.delete(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex
        except e.PrerecordingNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        return Response(None)
