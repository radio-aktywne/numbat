from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from emilounge.config.models import EmishowsConfig
from emilounge.services.emishows import models as m
from emilounge.services.emishows.serializer import Serializer


class Endpoint(BaseEndpoint):
    """Endpoints for emishows API."""

    EVENTS = "/events"
    SCHEDULE = "/schedule"


class BaseService(Gracy[Endpoint]):
    """Base class for emishows service."""

    def __init__(self, config: EmishowsConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = config.http.url
            SETTINGS = GracyConfig(
                retry=GracefulRetry(
                    delay=1,
                    max_attempts=3,
                    delay_modifier=2,
                ),
            )

        self.Config = Config

        super().__init__(*args, **kwargs)

        self._config = config


class EventsNamespace(GracyNamespace[Endpoint]):
    """Namespace for emishows events endpoint."""

    async def mget(self, request: m.EventsGetRequest) -> m.EventsGetResponse:
        """Get an event by ID."""

        id = request.id
        include = request.include

        params = {}
        if include is not None:
            params["include"] = Serializer(m.EventsGetRequestInclude).json(include)

        path = f"{Endpoint.EVENTS}/{id}"

        res = await self.get(path, params=params)

        event = m.Event.model_validate_json(res.content)

        return m.EventsGetResponse(
            event=event,
        )


class ScheduleNamespace(GracyNamespace[Endpoint]):
    """Namespace for emishows schedule endpoint."""

    async def list(self, request: m.ScheduleListRequest) -> m.ScheduleListResponse:
        """List schedules."""

        start = request.start
        end = request.end
        limit = request.limit
        offset = request.offset
        where = request.where
        include = request.include
        order = request.order

        params = {}
        if start is not None:
            params["start"] = Serializer(m.ScheduleListRequestStart).json(start)
        if end is not None:
            params["end"] = Serializer(m.ScheduleListRequestEnd).json(end)
        if limit is not None:
            params["limit"] = Serializer(m.ScheduleListRequestLimit).json(limit)
        if offset is not None:
            params["offset"] = Serializer(m.ScheduleListRequestOffset).json(offset)
        if where is not None:
            params["where"] = Serializer(m.ScheduleListRequestWhere).json(where)
        if include is not None:
            params["include"] = Serializer(m.ScheduleListRequestInclude).json(include)
        if order is not None:
            params["order"] = Serializer(m.ScheduleListRequestOrder).json(order)

        res = await self.get(Endpoint.SCHEDULE, params=params)

        results = m.ScheduleList.model_validate_json(res.content)

        return m.ScheduleListResponse(
            results=results,
        )


class EmishowsService(BaseService):
    """Service for emishows API."""

    events: EventsNamespace
    schedule: ScheduleNamespace
