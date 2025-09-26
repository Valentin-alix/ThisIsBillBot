from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildMissionStartListenerEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMissionStartListenerRequest(_message.Message):
    __slots__ = ("listener_options",)
    class GuildMissionListenerOptions(_message.Message):
        __slots__ = ("unknown_four_hundred_eighty_seven", "unknown_four_hundred_eighty_eight", "unknown_four_hundred_eighty_nine", "unknown_four_hundred_ninety")
        UNKNOWN_FOUR_HUNDRED_EIGHTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_EIGHTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_EIGHTY_NINE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_NINETY_FIELD_NUMBER: _ClassVar[int]
        unknown_four_hundred_eighty_seven: int
        unknown_four_hundred_eighty_eight: int
        unknown_four_hundred_eighty_nine: _containers.RepeatedScalarFieldContainer[int]
        unknown_four_hundred_ninety: bool
        def __init__(self, unknown_four_hundred_eighty_seven: _Optional[int] = ..., unknown_four_hundred_eighty_eight: _Optional[int] = ..., unknown_four_hundred_eighty_nine: _Optional[_Iterable[int]] = ..., unknown_four_hundred_ninety: bool = ...) -> None: ...
    LISTENER_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    listener_options: GuildMissionStartListenerRequest.GuildMissionListenerOptions
    def __init__(self, listener_options: _Optional[_Union[GuildMissionStartListenerRequest.GuildMissionListenerOptions, _Mapping]] = ...) -> None: ...

class GuildMissionStopListenerEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMissionStopListenerRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
