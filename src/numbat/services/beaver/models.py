from collections.abc import Sequence
from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from numbat.models.base import SerializableModel, datamodel
from numbat.utils.time import NaiveDatetime, Timezone


class EventType(StrEnum):
    """Event type options."""

    live = "live"
    replay = "replay"
    prerecorded = "prerecorded"


class Event(SerializableModel):
    """Event data."""

    id: UUID
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    timezone: Timezone
    """Timezone of the event."""


class EventInstance(SerializableModel):
    """Event instance data."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""

    end: NaiveDatetime
    """End datetime of the event instance in event timezone."""


class Schedule(SerializableModel):
    """Schedule data."""

    event: Event
    """Event data."""

    instances: Sequence[EventInstance]
    """Event instances."""


class ScheduleList(SerializableModel):
    """List of event schedules."""

    schedules: Sequence[Schedule]
    """Schedules that matched the request."""


class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: str


type EventsGetRequestId = UUID

type EventsGetResponseEvent = Event

type ScheduleListRequestStart = NaiveDatetime | None

type ScheduleListRequestEnd = NaiveDatetime | None

type ScheduleListRequestWhere = EventWhereInput | None

type ScheduleListResponseResults = ScheduleList


@datamodel
class EventsGetRequest:
    """Request to get an event."""

    id: EventsGetRequestId
    """Identifier of the event to get."""


@datamodel
class EventsGetResponse:
    """Response for getting an event."""

    event: EventsGetResponseEvent
    """Event that matched the request."""


@datamodel
class ScheduleListRequest:
    """Request to list schedules."""

    start: ScheduleListRequestStart
    """Start datetime in UTC to filter events instances."""

    end: ScheduleListRequestEnd
    """End datetime in UTC to filter events instances."""

    where: ScheduleListRequestWhere
    """Filter to apply to find events."""


@datamodel
class ScheduleListResponse:
    """Response for listing schedules."""

    results: ScheduleListResponseResults
    """List of schedules."""
