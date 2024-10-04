from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Choice(_message.Message):
    __slots__ = ("id", "position")
    ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    id: int
    position: int
    def __init__(self, id: _Optional[int] = ..., position: _Optional[int] = ...) -> None: ...

class VotedChoice(_message.Message):
    __slots__ = ("id", "position", "players")
    ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    id: int
    position: int
    players: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., position: _Optional[int] = ..., players: _Optional[_Iterable[int]] = ...) -> None: ...

class ChoiceSelectionEvent(_message.Message):
    __slots__ = ("selection_id", "choices")
    SELECTION_ID_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    selection_id: int
    choices: _containers.RepeatedCompositeFieldContainer[Choice]
    def __init__(self, selection_id: _Optional[int] = ..., choices: _Optional[_Iterable[_Union[Choice, _Mapping]]] = ...) -> None: ...

class FightChoiceSelectionEvent(_message.Message):
    __slots__ = ("selection_id", "target_protocol_id", "choices")
    SELECTION_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_PROTOCOL_ID_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    selection_id: int
    target_protocol_id: int
    choices: _containers.RepeatedCompositeFieldContainer[Choice]
    def __init__(self, selection_id: _Optional[int] = ..., target_protocol_id: _Optional[int] = ..., choices: _Optional[_Iterable[_Union[Choice, _Mapping]]] = ...) -> None: ...

class ChoiceSelectedEvent(_message.Message):
    __slots__ = ("position",)
    POSITION_FIELD_NUMBER: _ClassVar[int]
    position: int
    def __init__(self, position: _Optional[int] = ...) -> None: ...

class ChoiceSelectedRequest(_message.Message):
    __slots__ = ("position",)
    POSITION_FIELD_NUMBER: _ClassVar[int]
    position: int
    def __init__(self, position: _Optional[int] = ...) -> None: ...

class CurrentGlobalChoiceSelectionEvent(_message.Message):
    __slots__ = ("selection_id", "choices")
    SELECTION_ID_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    selection_id: int
    choices: _containers.RepeatedCompositeFieldContainer[VotedChoice]
    def __init__(self, selection_id: _Optional[int] = ..., choices: _Optional[_Iterable[_Union[VotedChoice, _Mapping]]] = ...) -> None: ...

class GlobalChoiceSelectionEvent(_message.Message):
    __slots__ = ("selection_id", "choices")
    SELECTION_ID_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    selection_id: int
    choices: _containers.RepeatedCompositeFieldContainer[Choice]
    def __init__(self, selection_id: _Optional[int] = ..., choices: _Optional[_Iterable[_Union[Choice, _Mapping]]] = ...) -> None: ...

class GlobalChoiceSelectedRequest(_message.Message):
    __slots__ = ("position",)
    POSITION_FIELD_NUMBER: _ClassVar[int]
    position: int
    def __init__(self, position: _Optional[int] = ...) -> None: ...

class GlobalChoiceVoteEvent(_message.Message):
    __slots__ = ("player_id", "choice_position")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    CHOICE_POSITION_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    choice_position: int
    def __init__(self, player_id: _Optional[int] = ..., choice_position: _Optional[int] = ...) -> None: ...

class GlobalChoiceSelectedEvent(_message.Message):
    __slots__ = ("position",)
    POSITION_FIELD_NUMBER: _ClassVar[int]
    position: int
    def __init__(self, position: _Optional[int] = ...) -> None: ...
