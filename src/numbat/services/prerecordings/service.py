from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID

from numbat.services.amber import errors as ae
from numbat.services.amber import models as am
from numbat.services.amber.service import AmberService
from numbat.services.beaver import errors as be
from numbat.services.beaver import models as bm
from numbat.services.beaver.service import BeaverService
from numbat.services.prerecordings import errors as e
from numbat.services.prerecordings import models as m
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
        except ae.ServiceError as ex:
            raise e.AmberError from ex
        except be.ServiceError as ex:
            raise e.BeaverError from ex

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
                events_get_response = await self._beaver.events.get_by_id(
                    events_get_request
                )
            except be.ResponseError as ex:
                if ex.response.status_code == HTTPStatus.NOT_FOUND:
                    return None

                raise

        if events_get_response.event.type != bm.EventType.prerecorded:
            raise e.BadEventTypeError(events_get_response.event.type)

        return events_get_response.event

    async def _get_instance(
        self, event: UUID, start: datetime
    ) -> bm.EventInstance | None:
        mevent = await self._get_event(event)

        if mevent is None:
            return None

        utcstart = (
            start.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=mevent.timezone
            )
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        utcend = utcstart + timedelta(days=1)

        schedule_list_request = bm.ScheduleListRequest(
            start=utcstart, end=utcend, where={"id": str(mevent.id)}
        )

        with self._handle_errors():
            schedule_list_response = await self._beaver.schedule.list(
                schedule_list_request
            )

        schedule = next(iter(schedule_list_response.results.schedules), None)

        if schedule is None:
            return None

        if schedule.event.type != bm.EventType.prerecorded:
            raise e.BadEventTypeError(schedule.event.type)

        return next(
            (instance for instance in schedule.instances if instance.start == start),
            None,
        )

    def _make_prefix(self, event: UUID) -> str:
        return f"{event}/"

    def _make_name(self, start: datetime) -> str:
        return isostringify(start)

    def _make_key(self, event: UUID, start: datetime) -> str:
        prefix = self._make_prefix(event)
        name = self._make_name(start)
        return f"{prefix}{name}"

    def _parse_prefix(self, prefix: str) -> UUID:
        return UUID(prefix[:-1])

    def _parse_name(self, name: str) -> datetime:
        return isoparse(name)

    def _parse_key(self, key: str) -> tuple[UUID, datetime]:
        split = key.find("/")
        prefix, name = key[: split + 1], key[split + 1 :]
        event = self._parse_prefix(prefix)
        start = self._parse_name(name)
        return event, start

    async def _list_get_objects(self, prefix: str) -> Sequence[am.Object]:
        list_request = am.ListRequest(prefix=prefix, recursive=False)

        with self._handle_errors():
            list_response = await self._amber.list(list_request)
            return [obj async for obj in list_response.objects]

    def _list_map_objects(
        self, objects: Sequence[am.Object]
    ) -> Sequence[m.Prerecording]:
        prerecordings = []

        for obj in objects:
            event, start = self._parse_key(obj.name)
            prerecording = m.Prerecording(event=event, start=start)
            prerecordings.append(prerecording)

        return prerecordings

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

    def _list_filter_prerecordings(
        self,
        prerecordings: Sequence[m.Prerecording],
        after: datetime | None,
        before: datetime | None,
    ) -> Sequence[m.Prerecording]:
        if after is not None:
            prerecordings = [
                prerecording
                for prerecording in prerecordings
                if prerecording.start > after
            ]

        if before is not None:
            prerecordings = [
                prerecording
                for prerecording in prerecordings
                if prerecording.start < before
            ]

        return prerecordings

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
        if await self._get_event(request.event) is None:
            raise e.EventNotFoundError(request.event)

        prefix = self._make_prefix(request.event)

        objects = await self._list_get_objects(prefix)
        prerecordings = self._list_map_objects(objects)
        prerecordings = self._list_filter_prerecordings(
            prerecordings, request.after, request.before
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
        if await self._get_instance(request.event, request.start) is None:
            raise e.InstanceNotFoundError(request.event, request.start)

        key = self._make_key(request.event, request.start)

        download_request = am.DownloadRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(request.event, request.start),
        ):
            download_response = await self._amber.download(download_request)

        return m.DownloadResponse(content=download_response.content)

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a prerecording."""
        if await self._get_instance(request.event, request.start) is None:
            raise e.InstanceNotFoundError(request.event, request.start)

        key = self._make_key(request.event, request.start)

        upload_request = am.UploadRequest(name=key, content=request.content)

        with self._handle_errors():
            await self._amber.upload(upload_request)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a prerecording."""
        if await self._get_instance(request.event, request.start) is None:
            raise e.InstanceNotFoundError(request.event, request.start)

        key = self._make_key(request.event, request.start)

        delete_request = am.DeleteRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(request.event, request.start),
        ):
            await self._amber.delete(delete_request)

        return m.DeleteResponse()
