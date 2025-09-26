import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerSettingsEvent(_message.Message):
    __slots__ = ("language", "community", "game_type", "is_mono_account", "arena_leave_ban_time", "item_max_level", "has_free_autopilot")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    COMMUNITY_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_MONO_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    ARENA_LEAVE_BAN_TIME_FIELD_NUMBER: _ClassVar[int]
    ITEM_MAX_LEVEL_FIELD_NUMBER: _ClassVar[int]
    HAS_FREE_AUTOPILOT_FIELD_NUMBER: _ClassVar[int]
    language: str
    community: int
    game_type: _common_pb2.ServerType
    is_mono_account: bool
    arena_leave_ban_time: int
    item_max_level: int
    has_free_autopilot: bool
    def __init__(self, language: _Optional[str] = ..., community: _Optional[int] = ..., game_type: _Optional[_Union[_common_pb2.ServerType, str]] = ..., is_mono_account: bool = ..., arena_leave_ban_time: _Optional[int] = ..., item_max_level: _Optional[int] = ..., has_free_autopilot: bool = ...) -> None: ...

class ServerExperienceModifierEvent(_message.Message):
    __slots__ = ("experience_percentage",)
    EXPERIENCE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    experience_percentage: int
    def __init__(self, experience_percentage: _Optional[int] = ...) -> None: ...
