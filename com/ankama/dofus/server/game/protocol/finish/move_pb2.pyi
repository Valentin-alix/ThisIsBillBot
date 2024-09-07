from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FinishMovesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FinishMoveSetRequest(_message.Message):
    __slots__ = ("finish_move_id", "effective")
    FINISH_MOVE_ID_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
    finish_move_id: int
    effective: bool
    def __init__(self, finish_move_id: _Optional[int] = ..., effective: bool = ...) -> None: ...

class FinishMovesEvent(_message.Message):
    __slots__ = ("finish_moves",)
    class FinishMove(_message.Message):
        __slots__ = ("finish_move_id", "effective")
        FINISH_MOVE_ID_FIELD_NUMBER: _ClassVar[int]
        EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
        finish_move_id: int
        effective: bool
        def __init__(self, finish_move_id: _Optional[int] = ..., effective: bool = ...) -> None: ...
    FINISH_MOVES_FIELD_NUMBER: _ClassVar[int]
    finish_moves: _containers.RepeatedCompositeFieldContainer[FinishMovesEvent.FinishMove]
    def __init__(self, finish_moves: _Optional[_Iterable[_Union[FinishMovesEvent.FinishMove, _Mapping]]] = ...) -> None: ...
