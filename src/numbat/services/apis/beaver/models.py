from collections.abc import Sequence
from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from numbat.models.base import SerializableModel, datamodel
from numbat.utils.time import NaiveDatetime, Timedelta, Timezone, UTCDatetime


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


class Instance(SerializableModel):
    """Instance data."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""

    duration: Timedelta
    """Duration of the instance."""

    event: Event | None
    """Event the instance belongs to."""


class InstanceList(SerializableModel):
    """List of instances."""

    instances: Sequence[Instance]
    """Instances that matched the request."""


class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: UUID
    """Identifier of the event."""


EventRelationFilter = TypedDict(
    "EventRelationFilter",
    {
        "is": EventWhereInput,
        "is_not": EventWhereInput,
    },
    total=False,
)


class InstanceWhereInput(TypedDict, total=False):
    """Instance arguments for searching."""

    event: EventRelationFilter
    """Event relation filter."""


class InstanceInclude(TypedDict, total=False):
    """Relations to include when querying instances."""

    event: bool
    """Event relation to include."""


type EventsGetRequestId = UUID

type EventsGetResponseEvent = Event

type InstancesListRequestStart = UTCDatetime

type InstancesListRequestEnd = UTCDatetime

type InstancesListRequestWhere = InstanceWhereInput | None

type InstancesListRequestInclude = InstanceInclude | None

type InstancesListResponseResults = InstanceList

type InstancesGetRequestEventId = UUID

type InstancesGetRequestStart = NaiveDatetime

type InstancesGetRequestInclude = InstanceInclude | None

type InstancesGetResponseInstance = Instance


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
class InstancesListRequest:
    """Request to list instances."""

    start: InstancesListRequestStart
    """Start datetime in UTC to filter events instances."""

    end: InstancesListRequestEnd
    """End datetime in UTC to filter events instances."""

    where: InstancesListRequestWhere
    """Filter to apply to find events."""

    include: InstancesListRequestInclude
    """Relations to include in the response."""


@datamodel
class InstancesListResponse:
    """Response for listing instances."""

    results: InstancesListResponseResults
    """List of instances."""


@datamodel
class InstancesGetRequest:
    """Request to get an instance."""

    event_id: InstancesGetRequestEventId
    """Identifier of the event the instance to get belongs to."""

    start: InstancesGetRequestStart
    """Start datetime of the instance to get in event timezone."""

    include: InstancesGetRequestInclude
    """Relations to include in the response."""


@datamodel
class InstancesGetResponse:
    """Response for getting an instance."""

    instance: InstancesGetResponseInstance
    """Instance that matched the request."""
