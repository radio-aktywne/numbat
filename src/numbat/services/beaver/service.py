from typing import Any

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from numbat.config.models import BeaverConfig
from numbat.services.beaver import models as m
from numbat.services.beaver.serializer import Serializer


class Endpoint(BaseEndpoint):
    """Endpoints for beaver service."""

    EVENTS = "/events"
    SCHEDULE = "/schedule"


class BaseService(Gracy[Endpoint]):
    """Base class for beaver service."""

    def __init__(self, config: BeaverConfig, *args: Any, **kwargs: Any) -> None:
        self.Config.BASE_URL = config.http.url
        self.Config.SETTINGS = GracyConfig(
            retry=GracefulRetry(
                delay=1,
                max_attempts=3,
                delay_modifier=2,
            ),
        )
        super().__init__(*args, **kwargs)
        self._config = config


class EventsNamespace(GracyNamespace[Endpoint]):
    """Namespace for beaver events endpoint."""

    async def mget(self, request: m.EventsGetRequest) -> m.EventsGetResponse:
        """Get an event by ID."""
        event_id = request.id
        include = request.include

        params = {}
        if include is not None:
            params["include"] = Serializer[m.EventsGetRequestInclude].serialize(include)

        path = f"{Endpoint.EVENTS}/{event_id}"

        res = await self.get(path, params=params)

        event = m.Event.model_validate_json(res.content)

        return m.EventsGetResponse(
            event=event,
        )


class ScheduleNamespace(GracyNamespace[Endpoint]):
    """Namespace for beaver schedule endpoint."""

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
            params["start"] = Serializer[m.ScheduleListRequestStart].serialize(start)
        if end is not None:
            params["end"] = Serializer[m.ScheduleListRequestEnd].serialize(end)
        if limit is not None:
            params["limit"] = Serializer[m.ScheduleListRequestLimit].serialize(limit)
        if offset is not None:
            params["offset"] = Serializer[m.ScheduleListRequestOffset].serialize(offset)
        if where is not None:
            params["where"] = Serializer[m.ScheduleListRequestWhere].serialize(where)
        if include is not None:
            params["include"] = Serializer[m.ScheduleListRequestInclude].serialize(
                include
            )
        if order is not None:
            params["order"] = Serializer[m.ScheduleListRequestOrder].serialize(order)

        res = await self.get(Endpoint.SCHEDULE, params=params)

        results = m.ScheduleList.model_validate_json(res.content)

        return m.ScheduleListResponse(
            results=results,
        )


class BeaverService(BaseService):
    """Service for beaver service."""

    events: EventsNamespace
    schedule: ScheduleNamespace
