import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BreachTeleportRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachRoomUnlockRequest(_message.Message):
    __slots__ = ("room_id",)
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    room_id: int
    def __init__(self, room_id: _Optional[int] = ...) -> None: ...

class BreachExitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachRewardBuyRequest(_message.Message):
    __slots__ = ("reward_id",)
    REWARD_ID_FIELD_NUMBER: _ClassVar[int]
    reward_id: int
    def __init__(self, reward_id: _Optional[int] = ...) -> None: ...

class BreachInvitationRequest(_message.Message):
    __slots__ = ("guests",)
    GUESTS_FIELD_NUMBER: _ClassVar[int]
    guests: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, guests: _Optional[_Iterable[int]] = ...) -> None: ...

class BreachInvitationAnswerRequest(_message.Message):
    __slots__ = ("accepted",)
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    def __init__(self, accepted: bool = ...) -> None: ...

class BreachKickRequest(_message.Message):
    __slots__ = ("player_id",)
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    def __init__(self, player_id: _Optional[int] = ...) -> None: ...

class BreachEnterEvent(_message.Message):
    __slots__ = ("owner",)
    OWNER_FIELD_NUMBER: _ClassVar[int]
    owner: int
    def __init__(self, owner: _Optional[int] = ...) -> None: ...

class BreachTeleportResultEvent(_message.Message):
    __slots__ = ("teleported",)
    TELEPORTED_FIELD_NUMBER: _ClassVar[int]
    teleported: bool
    def __init__(self, teleported: bool = ...) -> None: ...

class BreachRoomLockedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachRoomUnlockResultEvent(_message.Message):
    __slots__ = ("room_id", "result")
    class BreachRoomUnlockResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[BreachRoomUnlockResultEvent.BreachRoomUnlockResult]
        FAIL_NOT_ENOUGH_BUDGET: _ClassVar[BreachRoomUnlockResultEvent.BreachRoomUnlockResult]
    SUCCESS: BreachRoomUnlockResultEvent.BreachRoomUnlockResult
    FAIL_NOT_ENOUGH_BUDGET: BreachRoomUnlockResultEvent.BreachRoomUnlockResult
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    room_id: int
    result: BreachRoomUnlockResultEvent.BreachRoomUnlockResult
    def __init__(self, room_id: _Optional[int] = ..., result: _Optional[_Union[BreachRoomUnlockResultEvent.BreachRoomUnlockResult, str]] = ...) -> None: ...

class BreachExitResultEvent(_message.Message):
    __slots__ = ("exited",)
    EXITED_FIELD_NUMBER: _ClassVar[int]
    exited: bool
    def __init__(self, exited: bool = ...) -> None: ...

class BreachStateEvent(_message.Message):
    __slots__ = ("owner", "bonuses", "budget", "saved")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    BONUSES_FIELD_NUMBER: _ClassVar[int]
    BUDGET_FIELD_NUMBER: _ClassVar[int]
    SAVED_FIELD_NUMBER: _ClassVar[int]
    owner: _common_pb2.Character
    bonuses: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    budget: int
    saved: bool
    def __init__(self, owner: _Optional[_Union[_common_pb2.Character, _Mapping]] = ..., bonuses: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ..., budget: _Optional[int] = ..., saved: bool = ...) -> None: ...

class BreachCharactersEvent(_message.Message):
    __slots__ = ("players",)
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    players: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, players: _Optional[_Iterable[int]] = ...) -> None: ...

class BreachBonusEvent(_message.Message):
    __slots__ = ("bonus",)
    BONUS_FIELD_NUMBER: _ClassVar[int]
    bonus: _common_pb2.ObjectEffect
    def __init__(self, bonus: _Optional[_Union[_common_pb2.ObjectEffect, _Mapping]] = ...) -> None: ...

class BreachBudgetEvent(_message.Message):
    __slots__ = ("budget",)
    BUDGET_FIELD_NUMBER: _ClassVar[int]
    budget: int
    def __init__(self, budget: _Optional[int] = ...) -> None: ...

class BreachSavedEvent(_message.Message):
    __slots__ = ("saved",)
    SAVED_FIELD_NUMBER: _ClassVar[int]
    saved: bool
    def __init__(self, saved: bool = ...) -> None: ...

class BreachBranchesEvent(_message.Message):
    __slots__ = ("branches",)
    BRANCHES_FIELD_NUMBER: _ClassVar[int]
    branches: _containers.RepeatedCompositeFieldContainer[_common_pb2.BreachBranch]
    def __init__(self, branches: _Optional[_Iterable[_Union[_common_pb2.BreachBranch, _Mapping]]] = ...) -> None: ...

class BreachRewardsEvent(_message.Message):
    __slots__ = ("rewards",)
    REWARDS_FIELD_NUMBER: _ClassVar[int]
    rewards: _containers.RepeatedCompositeFieldContainer[_common_pb2.BreachReward]
    def __init__(self, rewards: _Optional[_Iterable[_Union[_common_pb2.BreachReward, _Mapping]]] = ...) -> None: ...

class BreachRewardBoughtEvent(_message.Message):
    __slots__ = ("reward_id", "bought")
    REWARD_ID_FIELD_NUMBER: _ClassVar[int]
    BOUGHT_FIELD_NUMBER: _ClassVar[int]
    reward_id: int
    bought: bool
    def __init__(self, reward_id: _Optional[int] = ..., bought: bool = ...) -> None: ...

class BreachInvitationOfferEvent(_message.Message):
    __slots__ = ("host", "time_left_before_cancel")
    HOST_FIELD_NUMBER: _ClassVar[int]
    TIME_LEFT_BEFORE_CANCEL_FIELD_NUMBER: _ClassVar[int]
    host: _common_pb2.Character
    time_left_before_cancel: int
    def __init__(self, host: _Optional[_Union[_common_pb2.Character, _Mapping]] = ..., time_left_before_cancel: _Optional[int] = ...) -> None: ...

class BreachInvitationCloseEvent(_message.Message):
    __slots__ = ("host",)
    HOST_FIELD_NUMBER: _ClassVar[int]
    host: _common_pb2.Character
    def __init__(self, host: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...
