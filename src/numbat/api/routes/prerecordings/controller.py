from collections.abc import Mapping
from dataclasses import dataclass
from typing import Annotated, cast

from litestar import Controller as BaseController
from litestar import Request, handlers
from litestar.datastructures import ResponseHeader
from litestar.di import Provide
from litestar.openapi.spec import (
    OpenAPIFormat,
    OpenAPIMediaType,
    OpenAPIResponse,
    OpenAPIType,
    Operation,
    RequestBody,
    Schema,
)
from litestar.params import Parameter
from litestar.response import Response, Stream
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT

from numbat.api.exceptions import BadRequestException, NotFoundException
from numbat.api.routes.prerecordings import errors as e
from numbat.api.routes.prerecordings import models as m
from numbat.api.routes.prerecordings.service import Service
from numbat.models.base import Jsonable, Serializable
from numbat.services.entities.prerecordings.service import PrerecordingsService
from numbat.state import State


@dataclass
class DownloadOperation(Operation):
    """OpenAPI Operation for downloading a prerecording."""

    def __post_init__(self) -> None:
        if (
            self.responses
            and str(HTTP_200_OK) in self.responses
            and (response := self.responses[str(HTTP_200_OK)])
            and isinstance(response, OpenAPIResponse)
            and (content := response.content)
            and "*/*" in content
            and (schema := content["*/*"].schema)
            and isinstance(schema, Schema)
        ):
            schema.type = OpenAPIType.STRING
            schema.format = OpenAPIFormat.BINARY


@dataclass
class UploadOperation(Operation):
    """OpenAPI Operation for uploading a prerecording."""

    def __post_init__(self) -> None:
        self.request_body = RequestBody(
            content={
                "*/*": OpenAPIMediaType(
                    schema=Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.BINARY)
                )
            },
            required=True,
        )


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
        raises=[BadRequestException],
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
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.results))

    @handlers.get(
        "/{event:str}/{start:str}",
        summary="Download prerecording",
        status_code=HTTP_200_OK,
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                required=True,
                documentation_only=True,
            ),
        ],
        media_type="*/*",
        raises=[BadRequestException, NotFoundException],
        operation_class=DownloadOperation,
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
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.NotFoundError as ex:
            raise NotFoundException from ex

        def dump(value: Serializable) -> str:
            return str(value.model_dump(mode="json", round_trip=True))

        try:
            headers = {
                "Content-Type": dump(
                    Serializable[m.DownloadResponseType](response.type),
                ),
                "Content-Length": dump(
                    Serializable[m.DownloadResponseSize](response.size),
                ),
                "ETag": dump(
                    Serializable[m.DownloadResponseTag](response.tag),
                ),
                "Last-Modified": dump(
                    Serializable[m.DownloadResponseModified](response.modified),
                ),
            }

            return Stream(response.data, headers=headers)
        except:
            await response.data.aclose()
            raise

    @handlers.head(
        "/{event:str}/{start:str}",
        summary="Download prerecording headers",
        response_description="Request fulfilled, headers follow",
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                required=True,
                documentation_only=True,
            ),
        ],
        raises=[BadRequestException, NotFoundException],
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
    ) -> None:
        """Download prerecording headers."""
        request = m.HeadDownloadRequest(event=event.root, start=start.root)

        try:
            response = await service.headdownload(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.NotFoundError as ex:
            raise NotFoundException from ex

        def dump(value: Serializable) -> str:
            return str(value.model_dump(mode="json", round_trip=True))

        headers = {
            "Content-Type": dump(
                Serializable[m.HeadDownloadResponseType](response.type),
            ),
            "Content-Length": dump(
                Serializable[m.HeadDownloadResponseSize](response.size),
            ),
            "ETag": dump(
                Serializable[m.HeadDownloadResponseTag](response.tag),
            ),
            "Last-Modified": dump(
                Serializable[m.HeadDownloadResponseModified](response.modified),
            ),
        }

        return cast("None", Response(None, headers=headers))

    @handlers.put(
        "/{event:str}/{start:str}",
        summary="Upload prerecording",
        status_code=HTTP_204_NO_CONTENT,
        raises=[BadRequestException],
        operation_class=UploadOperation,
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
    ) -> None:
        """Upload a prerecording."""
        data = request.stream()

        try:
            req = m.UploadRequest(
                event=event.root, start=start.root, type=content_type.root, data=data
            )

            try:
                await service.upload(req)
            except e.ValidationError as ex:
                raise BadRequestException from ex
        finally:
            await data.aclose()

    @handlers.delete(
        "/{event:str}/{start:str}",
        summary="Delete prerecording",
        raises=[BadRequestException, NotFoundException],
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
    ) -> None:
        """Delete a prerecording."""
        request = m.DeleteRequest(event=event.root, start=start.root)

        try:
            await service.delete(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.NotFoundError as ex:
            raise NotFoundException from ex
