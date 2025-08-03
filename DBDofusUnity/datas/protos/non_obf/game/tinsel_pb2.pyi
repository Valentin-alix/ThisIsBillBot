from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TinselSelectError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED: _ClassVar[TinselSelectError]
    INVALID: _ClassVar[TinselSelectError]
    ALREADY: _ClassVar[TinselSelectError]
UNDEFINED: TinselSelectError
INVALID: TinselSelectError
ALREADY: TinselSelectError

class TitlesAndOrnamentsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TitlesAndOrnamentsEvent(_message.Message):
    __slots__ = ("titles", "ornaments")
    TITLES_FIELD_NUMBER: _ClassVar[int]
    ORNAMENTS_FIELD_NUMBER: _ClassVar[int]
    titles: _containers.RepeatedScalarFieldContainer[int]
    ornaments: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, titles: _Optional[_Iterable[int]] = ..., ornaments: _Optional[_Iterable[int]] = ...) -> None: ...

class TitleGainedEvent(_message.Message):
    __slots__ = ("title_id",)
    TITLE_ID_FIELD_NUMBER: _ClassVar[int]
    title_id: int
    def __init__(self, title_id: _Optional[int] = ...) -> None: ...

class TitleLostEvent(_message.Message):
    __slots__ = ("title_id",)
    TITLE_ID_FIELD_NUMBER: _ClassVar[int]
    title_id: int
    def __init__(self, title_id: _Optional[int] = ...) -> None: ...

class OrnamentGainedEvent(_message.Message):
    __slots__ = ("ornament_id",)
    ORNAMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ornament_id: int
    def __init__(self, ornament_id: _Optional[int] = ...) -> None: ...

class OrnamentLostEvent(_message.Message):
    __slots__ = ("ornament_id",)
    ORNAMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ornament_id: int
    def __init__(self, ornament_id: _Optional[int] = ...) -> None: ...

class TitleSelectedEvent(_message.Message):
    __slots__ = ("title_id",)
    TITLE_ID_FIELD_NUMBER: _ClassVar[int]
    title_id: int
    def __init__(self, title_id: _Optional[int] = ...) -> None: ...

class TitleSelectErrorEvent(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: TinselSelectError
    def __init__(self, reason: _Optional[_Union[TinselSelectError, str]] = ...) -> None: ...

class OrnamentSelectedEvent(_message.Message):
    __slots__ = ("ornament_id",)
    ORNAMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ornament_id: int
    def __init__(self, ornament_id: _Optional[int] = ...) -> None: ...

class OrnamentSelectErrorEvent(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: TinselSelectError
    def __init__(self, reason: _Optional[_Union[TinselSelectError, str]] = ...) -> None: ...
