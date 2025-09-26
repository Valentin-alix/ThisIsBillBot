from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CalendarRequest(_message.Message):
    __slots__ = ("start_date", "end_date")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    start_date: str
    end_date: str
    def __init__(self, start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class CalendarEvent(_message.Message):
    __slots__ = ("krosmic_events", "festivity_events")
    KROSMIC_EVENTS_FIELD_NUMBER: _ClassVar[int]
    FESTIVITY_EVENTS_FIELD_NUMBER: _ClassVar[int]
    krosmic_events: _containers.RepeatedCompositeFieldContainer[CalendarOccurrence]
    festivity_events: _containers.RepeatedCompositeFieldContainer[CalendarEntry]
    def __init__(self, krosmic_events: _Optional[_Iterable[_Union[CalendarOccurrence, _Mapping]]] = ..., festivity_events: _Optional[_Iterable[_Union[CalendarEntry, _Mapping]]] = ...) -> None: ...

class CalendarOccurrence(_message.Message):
    __slots__ = ("event_uuid", "description_id", "end_date", "start_date")
    EVENT_UUID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    event_uuid: str
    description_id: int
    end_date: str
    start_date: str
    def __init__(self, event_uuid: _Optional[str] = ..., description_id: _Optional[int] = ..., end_date: _Optional[str] = ..., start_date: _Optional[str] = ...) -> None: ...

class CalendarEntry(_message.Message):
    __slots__ = ("start_date", "end_date", "description_id")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    start_date: str
    end_date: str
    description_id: int
    def __init__(self, start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., description_id: _Optional[int] = ...) -> None: ...
