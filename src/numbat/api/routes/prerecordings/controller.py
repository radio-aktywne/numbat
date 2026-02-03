from collections.abc import AsyncGenerator, Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import Request, handlers
from litestar.datastructures import ResponseHeader
from litestar.di import Provide
from litestar.exceptions import InternalServerException
from litestar.openapi import ResponseSpec
from litestar.params import Parameter
from litestar.response import Response, Stream
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT

from numbat.api.exceptions import BadRequestException, NotFoundException
from numbat.api.routes.prerecordings import errors as e
from numbat.api.routes.prerecordings import models as m
from numbat.api.routes.prerecordings.service import Service
from numbat.models.base import Jsonable, Serializable
from numbat.services.prerecordings.service import PrerecordingsService
from numbat.state import State
from numbat.utils.time import httpstringify


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            prerecordings=PrerecordingsService(amber=state.amber, beaver=state.beaver)
        )

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the prerecordings endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        "/{event:str}",
        summary="List prerecordings",
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        event: Annotated[
            Serializable[m.ListRequestEvent],
            Parameter(
                description="Identifier of the event to list prerecordings for.",
            ),
        ],
        after: Annotated[
            Jsonable[m.ListRequestAfter] | None,
            Parameter(
                description="Only list prerecordings after this datetime (in event timezone).",
            ),
        ] = None,
        before: Annotated[
            Jsonable[m.ListRequestBefore] | None,
            Parameter(
                description="Only list prerecordings before this datetime (in event timezone).",
            ),
        ] = None,
        limit: Annotated[
            Jsonable[m.ListRequestLimit] | None,
            Parameter(
                description="Maximum number of prerecordings to return. Default is 10.",
            ),
        ] = None,
        offset: Annotated[
            Jsonable[m.ListRequestOffset] | None,
            Parameter(
                description="Number of prerecordings to skip.",
            ),
        ] = None,
        order: Annotated[
            Jsonable[m.ListRequestOrder] | None,
            Parameter(
                description="Order to apply to the results.",
            ),
        ] = None,
    ) -> Response[Serializable[m.ListResponseResults]]:
        """List prerecordings."""
        request = m.ListRequest(
            event=event.root,
            after=after.root if after else None,
            before=before.root if before else None,
            limit=limit.root if limit else 10,
            offset=offset.root if offset else None,
            order=order.root if order else None,
        )

        try:
            response = await service.list(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.results))

    @handlers.get(
        "/{event:str}/{start:str}",
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
        responses={
            HTTP_200_OK: ResponseSpec(
                Stream,
                description="Request fulfilled, stream follows",
                generate_examples=False,
                media_type="*/*",
            )
        },
    )
    async def download(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.DownloadRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.DownloadRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> Stream:
        """Download a prerecording."""
        request = m.DownloadRequest(event=event.root, start=start.root)

        try:
            response = await service.download(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.PrerecordingNotFoundError as ex:
            raise NotFoundException from ex

        return Stream(
            response.data,
            headers={
                "Content-Type": response.type,
                "Content-Length": str(response.size),
                "ETag": response.tag,
                "Last-Modified": httpstringify(response.modified),
            },
        )

    @handlers.head(
        "/{event:str}/{start:str}",
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
        responses={
            HTTP_200_OK: ResponseSpec(
                None, description="Request fulfilled, nothing follows"
            )
        },
    )
    async def headdownload(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.HeadDownloadRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.HeadDownloadRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> Response[None]:
        """Download prerecording headers."""
        request = m.HeadDownloadRequest(event=event.root, start=start.root)

        try:
            response = await service.headdownload(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.PrerecordingNotFoundError as ex:
            raise NotFoundException from ex

        return Response(
            None,
            headers={
                "Content-Type": response.type,
                "Content-Length": str(response.size),
                "ETag": response.tag,
                "Last-Modified": httpstringify(response.modified),
            },
        )

    @handlers.put(
        "/{event:str}/{start:str}",
        summary="Upload prerecording",
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                None, description="Request fulfilled, nothing follows"
            )
        },
    )
    async def upload(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.UploadRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.UploadRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
        content_type: Annotated[
            Jsonable[m.UploadRequestType],
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

        req = m.UploadRequest(
            event=event.root,
            start=start.root,
            type=content_type.root,
            data=_stream(request),
        )

        try:
            await service.upload(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex

        return Response(None)

    @handlers.delete(
        "/{event:str}/{start:str}",
        summary="Delete prerecording",
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                None, description="Request fulfilled, nothing follows"
            )
        },
    )
    async def delete(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.DeleteRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.DeleteRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> Response[None]:
        """Delete a prerecording."""
        request = m.DeleteRequest(event=event.root, start=start.root)

        try:
            await service.delete(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.PrerecordingNotFoundError as ex:
            raise NotFoundException from ex

        return Response(None)
