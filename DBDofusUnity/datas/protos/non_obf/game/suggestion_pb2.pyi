from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ActivitySuggestionsRequest(_message.Message):
    __slots__ = ("min_level", "max_level", "area_id", "activity_category_id", "cards_number")
    MIN_LEVEL_FIELD_NUMBER: _ClassVar[int]
    MAX_LEVEL_FIELD_NUMBER: _ClassVar[int]
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    CARDS_NUMBER_FIELD_NUMBER: _ClassVar[int]
    min_level: int
    max_level: int
    area_id: int
    activity_category_id: int
    cards_number: int
    def __init__(self, min_level: _Optional[int] = ..., max_level: _Optional[int] = ..., area_id: _Optional[int] = ..., activity_category_id: _Optional[int] = ..., cards_number: _Optional[int] = ...) -> None: ...

class ActivityHideRequest(_message.Message):
    __slots__ = ("activity_id",)
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    activity_id: int
    def __init__(self, activity_id: _Optional[int] = ...) -> None: ...

class ActivityLockRequest(_message.Message):
    __slots__ = ("activity_id",)
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    activity_id: int
    def __init__(self, activity_id: _Optional[int] = ...) -> None: ...

class ActivitySuggestionsEvent(_message.Message):
    __slots__ = ("locked_activities", "unlocked_activities")
    LOCKED_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    UNLOCKED_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    locked_activities: _containers.RepeatedScalarFieldContainer[int]
    unlocked_activities: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, locked_activities: _Optional[_Iterable[int]] = ..., unlocked_activities: _Optional[_Iterable[int]] = ...) -> None: ...
