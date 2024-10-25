from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConsoleCommand(_message.Message):
    __slots__ = ("content", "quiet")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    QUIET_FIELD_NUMBER: _ClassVar[int]
    content: str
    quiet: bool
    def __init__(self, content: _Optional[str] = ..., quiet: bool = ...) -> None: ...

class ConsoleEnd(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ConsoleMessage(_message.Message):
    __slots__ = ("content", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TEXT: _ClassVar[ConsoleMessage.Type]
        INFO: _ClassVar[ConsoleMessage.Type]
        ERROR: _ClassVar[ConsoleMessage.Type]
    TEXT: ConsoleMessage.Type
    INFO: ConsoleMessage.Type
    ERROR: ConsoleMessage.Type
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    content: str
    type: ConsoleMessage.Type
    def __init__(self, content: _Optional[str] = ..., type: _Optional[_Union[ConsoleMessage.Type, str]] = ...) -> None: ...

class CommandSummary(_message.Message):
    __slots__ = ("command",)
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    command: _containers.RepeatedCompositeFieldContainer[Command]
    def __init__(self, command: _Optional[_Iterable[_Union[Command, _Mapping]]] = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ("alias", "arguments", "description")
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    alias: str
    arguments: str
    description: str
    def __init__(self, alias: _Optional[str] = ..., arguments: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
