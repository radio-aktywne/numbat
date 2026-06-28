import asyncio
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from uuid import UUID

from numbat.services.apis.beaver import errors as be
from numbat.services.apis.beaver import models as bm
from numbat.services.apis.beaver.service import BeaverService
from numbat.services.data.amber import errors as ae
from numbat.services.data.amber import models as am
from numbat.services.data.amber.service import AmberService
from numbat.services.entities.prerecordings import errors as e
from numbat.services.entities.prerecordings import models as m
from numbat.services.entities.prerecordings.utils import ContentTypeChecker
from numbat.utils.mime import MimeType, MimeTypeValidationError
from numbat.utils.time import isoparse, isostringify


class PrerecordingsService:
    """Service to manage prerecordings."""

    def __init__(self, amber: AmberService, beaver: BeaverService) -> None:
        self._amber = amber
        self._beaver = beaver

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except (ae.ServiceError, be.ServiceError) as ex:
            raise e.ServiceError from ex

    @contextmanager
    def _handle_not_found(self, event: UUID, start: datetime) -> Generator[None]:
        try:
            yield
        except ae.NotFoundError as ex:
            raise e.PrerecordingNotFoundError(event, start) from ex

    async def _get_event(self, event: UUID) -> bm.Event | None:
        events_get_request = bm.EventsGetRequest(id=event)

        with self._handle_errors():
            try:
                events_get_response = await self._beaver.events.get(events_get_request)
            except be.NotFoundError:
                return None

        return events_get_response.event

    async def _get_event_instances(
        self, event: bm.Event, after: datetime, before: datetime
    ) -> Sequence[bm.Instance]:
        utcafter = after.replace(tzinfo=event.timezone).astimezone(UTC)
        utcbefore = before.replace(tzinfo=event.timezone).astimezone(UTC)

        instances_list_request = bm.InstancesListRequest(
            start=utcafter,
            end=utcbefore,
            where={"event": {"is": {"id": event.id}}},
            include={"event": True},
        )

        with self._handle_errors():
            instances_list_response = await self._beaver.instances.list(
                instances_list_request
            )

        return instances_list_response.results.instances

    async def _get_instance(self, event: UUID, start: datetime) -> bm.Instance | None:
        instances_get_request = bm.InstancesGetRequest(
            event_id=event, start=start, include={"event": True}
        )

        with self._handle_errors():
            try:
                instances_get_response = await self._beaver.instances.get(
                    instances_get_request
                )
            except be.NotFoundError:
                return None

        return instances_get_response.instance

    async def _get_object(self, name: str) -> am.ObjectDetails | None:
        get_request = am.GetRequest(name=name)

        with self._handle_errors():
            try:
                get_response = await self._amber.get(get_request)
            except ae.NotFoundError:
                return None

        return get_response.object

    def _make_prefix(self, event: UUID) -> str:
        return f"{event}/"

    def _make_name(self, start: datetime) -> str:
        return isostringify(start)

    def _make_key(self, event: UUID, start: datetime) -> str:
        prefix = self._make_prefix(event)
        name = self._make_name(start)
        return f"{prefix}{name}"

    def _parse_prefix(self, prefix: str) -> UUID | None:
        try:
            return UUID(prefix[:-1])
        except ValueError:
            return None

    def _parse_name(self, name: str) -> datetime | None:
        try:
            return isoparse(name)
        except ValueError:
            return None

    def _parse_key(self, key: str) -> tuple[UUID, datetime] | None:
        split = key.find("/")
        prefix, name = key[: split + 1], key[split + 1 :]
        event = self._parse_prefix(prefix)
        start = self._parse_name(name)

        return (event, start) if event and start else None

    def _parse_content_type(self, value: str | None) -> MimeType | None:
        if value is None:
            return None

        try:
            parsed = MimeType.parse(value)
        except MimeTypeValidationError:
            return None

        return parsed if ContentTypeChecker().check(parsed) else None

    async def _list_get_objects(self, prefix: str) -> Sequence[am.ObjectListing]:
        list_request = am.ListRequest(prefix=prefix, recursive=False)

        with self._handle_errors():
            list_response = await self._amber.list(list_request)
            return [obj async for obj in list_response.objects]

    def _list_map_objects(
        self, objects: Sequence[am.ObjectListing]
    ) -> Sequence[m.Prerecording]:
        return [
            m.Prerecording(event=event, start=start)
            for obj in objects
            if (parsed := self._parse_key(obj.name))
            for event, start in [parsed]
        ]

    def _list_filter_prerecordings_by_time(
        self,
        prerecordings: Sequence[m.Prerecording],
        after: datetime | None,
        before: datetime | None,
    ) -> Sequence[m.Prerecording]:
        return [
            prerecording
            for prerecording in prerecordings
            if (after is None or prerecording.start >= after)
            and (before is None or prerecording.start < before)
        ]

    async def _list_filter_prerecordings_by_instance(
        self, prerecordings: Sequence[m.Prerecording], event: bm.Event
    ) -> Sequence[m.Prerecording]:
        after = min(prerecording.start for prerecording in prerecordings)
        after = after.replace(hour=0, minute=0, second=0, microsecond=0)

        before = max(prerecording.start for prerecording in prerecordings)
        before = before.replace(hour=0, minute=0, second=0, microsecond=0)
        before = before + timedelta(days=1)

        instances = await self._get_event_instances(event, after, before)
        starts = {instance.start for instance in instances}

        return [
            prerecording
            for prerecording in prerecordings
            if prerecording.start in starts
        ]

    async def _list_filter_prerecordings_by_content_type(
        self, prerecordings: Sequence[m.Prerecording]
    ) -> Sequence[m.Prerecording]:
        semaphore = asyncio.Semaphore(10)

        async def get(prerecording: m.Prerecording) -> am.ObjectDetails | None:
            key = self._make_key(prerecording.event, prerecording.start)

            async with semaphore:
                return await self._get_object(key)

        details = await asyncio.gather(
            *[get(prerecording) for prerecording in prerecordings]
        )

        return [
            prerecording
            for prerecording, detail in zip(prerecordings, details, strict=False)
            if detail and self._parse_content_type(detail.type)
        ]

    async def _list_filter_prerecordings(
        self,
        prerecordings: Sequence[m.Prerecording],
        event: bm.Event,
        after: datetime | None,
        before: datetime | None,
    ) -> Sequence[m.Prerecording]:
        prerecordings = self._list_filter_prerecordings_by_time(
            prerecordings, after, before
        )

        if not prerecordings:
            return []

        prerecordings = await self._list_filter_prerecordings_by_instance(
            prerecordings, event
        )

        if not prerecordings:
            return []

        return await self._list_filter_prerecordings_by_content_type(prerecordings)

    def _list_sort_prerecordings(
        self, prerecordings: Sequence[m.Prerecording], order: m.ListOrder | None
    ) -> Sequence[m.Prerecording]:
        if order is None:
            return prerecordings

        return sorted(
            prerecordings,
            key=lambda prerecording: prerecording.start,
            reverse=order == m.ListOrder.DESCENDING,
        )

    def _list_pick_prerecordings(
        self,
        prerecordings: Sequence[m.Prerecording],
        limit: int | None,
        offset: int | None,
    ) -> Sequence[m.Prerecording]:
        if offset is not None:
            prerecordings = prerecordings[offset:]

        if limit is not None:
            prerecordings = prerecordings[:limit]

        return prerecordings

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List prerecordings."""
        event = await self._get_event(request.event)

        if not event:
            raise e.EventNotFoundError(request.event)

        if event.type != bm.EventType.prerecorded:
            raise e.BadEventTypeError(event.type)

        prefix = self._make_prefix(event.id)

        objects = await self._list_get_objects(prefix)
        prerecordings = self._list_map_objects(objects)
        prerecordings = await self._list_filter_prerecordings(
            prerecordings, event, request.after, request.before
        )
        prerecordings = self._list_sort_prerecordings(prerecordings, request.order)

        count = len(prerecordings)

        prerecordings = self._list_pick_prerecordings(
            prerecordings, request.limit, request.offset
        )

        return m.ListResponse(
            count=count,
            limit=request.limit,
            offset=request.offset,
            prerecordings=prerecordings,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a prerecording."""
        instance = await self._get_instance(request.event, request.start)

        if not instance:
            raise e.InstanceNotFoundError(request.event, request.start)

        if instance.event is None:
            raise e.ServiceError

        if instance.event.type != bm.EventType.prerecorded:
            raise e.BadEventTypeError(instance.event.type)

        key = self._make_key(instance.event.id, instance.start)

        download_request = am.DownloadRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(instance.event.id, instance.start),
        ):
            download_response = await self._amber.download(download_request)

        try:
            content_type = self._parse_content_type(download_response.content.type)

            if content_type is None:
                raise e.PrerecordingNotFoundError(instance.event.id, instance.start)

            return m.DownloadResponse(
                content=m.DownloadContent(
                    type=content_type,
                    size=download_response.content.size,
                    tag=download_response.content.tag,
                    modified=download_response.content.modified,
                    data=download_response.content.data,
                )
            )
        except:
            await download_response.content.data.aclose()
            raise

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a prerecording."""
        instance = await self._get_instance(request.event, request.start)

        if not instance:
            raise e.InstanceNotFoundError(request.event, request.start)

        if instance.event is None:
            raise e.ServiceError

        if instance.event.type != bm.EventType.prerecorded:
            raise e.BadEventTypeError(instance.event.type)

        if not ContentTypeChecker().check(request.content.type):
            raise e.UnsupportedContentTypeError(request.content.type)

        key = self._make_key(instance.event.id, instance.start)

        upload_request = am.UploadRequest(
            name=key,
            content=am.UploadContent(
                type=str(request.content.type), data=request.content.data
            ),
        )

        with self._handle_errors():
            await self._amber.upload(upload_request)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a prerecording."""
        instance = await self._get_instance(request.event, request.start)

        if not instance:
            raise e.InstanceNotFoundError(request.event, request.start)

        if instance.event is None:
            raise e.ServiceError

        if instance.event.type != bm.EventType.prerecorded:
            raise e.BadEventTypeError(instance.event.type)

        key = self._make_key(instance.event.id, instance.start)

        get_request = am.GetRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(instance.event.id, instance.start),
        ):
            get_response = await self._amber.get(get_request)

        if not self._parse_content_type(get_response.object.type):
            raise e.PrerecordingNotFoundError(instance.event.id, instance.start)

        delete_request = am.DeleteRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(instance.event.id, instance.start),
        ):
            await self._amber.delete(delete_request)

        return m.DeleteResponse()
