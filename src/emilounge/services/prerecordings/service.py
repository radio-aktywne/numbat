from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID

from zoneinfo import ZoneInfo

from emilounge.services.emishows import errors as ee
from emilounge.services.emishows import models as em
from emilounge.services.emishows.service import EmishowsService
from emilounge.services.medialounge import errors as me
from emilounge.services.medialounge import models as mm
from emilounge.services.medialounge.service import MedialoungeService
from emilounge.services.prerecordings import errors as e
from emilounge.services.prerecordings import models as m


class PrerecordingsService:
    """Service to manage prerecordings."""

    def __init__(self, emishows: EmishowsService, medialounge: MedialoungeService):
        self._emishows = emishows
        self._medialounge = medialounge

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ee.ServiceError as ex:
            raise e.EmishowsError(str(ex)) from ex
        except me.ServiceError as ex:
            raise e.MedialoungeError(str(ex)) from ex

    @contextmanager
    def _handle_not_found(self, event: UUID, start: datetime) -> Generator[None]:
        try:
            yield
        except me.NotFoundError as ex:
            raise e.PrerecordingNotFoundError(event, start) from ex

    async def _get_event(self, event: UUID) -> em.Event | None:
        req = em.EventsGetRequest(
            id=event,
            include=None,
        )

        with self._handle_errors():
            try:
                res = await self._emishows.events.mget(req)
            except ee.ServiceError as ex:
                if hasattr(ex, "response"):
                    if ex.response.status_code == HTTPStatus.NOT_FOUND:
                        return None

                raise

        ev = res.event

        if ev.type != em.EventType.prerecorded:
            raise e.BadEventTypeError(ev.type)

        return ev

    async def _get_instance(
        self, event: UUID, start: datetime
    ) -> em.EventInstance | None:
        mevent = await self._get_event(event)

        if mevent is None:
            return None

        tz = ZoneInfo(mevent.timezone)
        utcstart = start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
        utcstart = utcstart.astimezone(UTC).replace(tzinfo=None)
        utcend = utcstart + timedelta(days=1)

        req = em.ScheduleListRequest(
            start=utcstart,
            end=utcend,
            limit=None,
            offset=None,
            where={
                "id": str(mevent.id),
            },
            include=None,
            order=None,
        )

        with self._handle_errors():
            res = await self._emishows.schedule.list(req)

        schedules = res.results.schedules

        schedule = next(iter(schedules), None)

        if schedule is None:
            return None

        if schedule.event.type != em.EventType.prerecorded:
            raise e.BadEventTypeError(schedule.event.type)

        return next(
            (instance for instance in schedule.instances if instance.start == start),
            None,
        )

    def _make_prefix(self, event: UUID) -> str:
        return f"{event}/"

    def _make_name(self, start: datetime) -> str:
        return start.isoformat()

    def _make_key(self, event: UUID, start: datetime) -> str:
        prefix = self._make_prefix(event)
        name = self._make_name(start)
        return f"{prefix}{name}"

    def _parse_prefix(self, prefix: str) -> UUID:
        return UUID(prefix[:-1])

    def _parse_name(self, name: str) -> datetime:
        return datetime.fromisoformat(name)

    def _parse_key(self, key: str) -> tuple[UUID, datetime]:
        split = key.find("/")
        prefix, name = key[: split + 1], key[split + 1 :]
        event = self._parse_prefix(prefix)
        start = self._parse_name(name)
        return event, start

    async def _list_get_objects(self, prefix: str) -> list[mm.Object]:
        req = mm.ListRequest(
            prefix=prefix,
            recursive=False,
        )

        with self._handle_errors():
            res = await self._medialounge.list(req)
            return [object async for object in res.objects]

    def _list_map_objects(self, objects: list[mm.Object]) -> list[m.Prerecording]:
        prerecordings = []

        for object in objects:
            event, start = self._parse_key(object.name)

            prerecording = m.Prerecording(
                event=event,
                start=start,
            )

            prerecordings.append(prerecording)

        return prerecordings

    def _list_sort_prerecordings(
        self, prerecordings: list[m.Prerecording], order: m.ListOrder | None
    ) -> list[m.Prerecording]:
        if order is None:
            return prerecordings

        return sorted(
            prerecordings,
            key=lambda prerecording: prerecording.start,
            reverse=order == m.ListOrder.DESCENDING,
        )

    def _list_filter_prerecordings(
        self,
        prerecordings: list[m.Prerecording],
        after: datetime | None,
        before: datetime | None,
    ) -> list[m.Prerecording]:
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
        self, prerecordings: list[m.Prerecording], limit: int | None, offset: int | None
    ) -> list[m.Prerecording]:
        if offset is not None:
            prerecordings = prerecordings[offset:]

        if limit is not None:
            prerecordings = prerecordings[:limit]

        return prerecordings

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List prerecordings."""

        event = request.event
        after = request.after
        before = request.before
        limit = request.limit
        offset = request.offset
        order = request.order

        if await self._get_event(event) is None:
            raise e.EventNotFoundError(event)

        prefix = self._make_prefix(event)

        objects = await self._list_get_objects(prefix)
        prerecordings = self._list_map_objects(objects)
        prerecordings = self._list_filter_prerecordings(prerecordings, after, before)
        prerecordings = self._list_sort_prerecordings(prerecordings, order)

        count = len(prerecordings)

        prerecordings = self._list_pick_prerecordings(prerecordings, limit, offset)

        return m.ListResponse(
            count=count,
            limit=limit,
            offset=offset,
            prerecordings=prerecordings,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a prerecording."""

        event = request.event
        start = request.start

        if await self._get_instance(event, start) is None:
            raise e.InstanceNotFoundError(event, start)

        key = self._make_key(event, start)

        req = mm.DownloadRequest(
            name=key,
        )

        with self._handle_errors():
            with self._handle_not_found(event, start):
                res = await self._medialounge.download(req)

        content = res.content

        return m.DownloadResponse(
            content=content,
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a prerecording."""

        event = request.event
        start = request.start
        content = request.content

        if await self._get_instance(event, start) is None:
            raise e.InstanceNotFoundError(event, start)

        key = self._make_key(event, start)

        req = mm.UploadRequest(
            name=key,
            content=content,
        )

        with self._handle_errors():
            await self._medialounge.upload(req)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a prerecording."""

        event = request.event
        start = request.start

        if await self._get_instance(event, start) is None:
            raise e.InstanceNotFoundError(event, start)

        key = self._make_key(event, start)

        req = mm.DeleteRequest(
            name=key,
        )

        with self._handle_errors():
            with self._handle_not_found(event, start):
                await self._medialounge.delete(req)

        return m.DeleteResponse()
