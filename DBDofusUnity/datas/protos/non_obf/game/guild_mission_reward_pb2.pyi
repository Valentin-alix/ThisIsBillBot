import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildMissionRewardsEvent(_message.Message):
    __slots__ = ("rewards",)
    class GuildMissionRewardList(_message.Message):
        __slots__ = ("unknown_four_hundred_ninety_one", "rewards")
        UNKNOWN_FOUR_HUNDRED_NINETY_ONE_FIELD_NUMBER: _ClassVar[int]
        REWARDS_FIELD_NUMBER: _ClassVar[int]
        unknown_four_hundred_ninety_one: int
        rewards: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectGidWithQuantity]
        def __init__(self, unknown_four_hundred_ninety_one: _Optional[int] = ..., rewards: _Optional[_Iterable[_Union[_common_pb2.ObjectGidWithQuantity, _Mapping]]] = ...) -> None: ...
    REWARDS_FIELD_NUMBER: _ClassVar[int]
    rewards: GuildMissionRewardsEvent.GuildMissionRewardList
    def __init__(self, rewards: _Optional[_Union[GuildMissionRewardsEvent.GuildMissionRewardList, _Mapping]] = ...) -> None: ...

class GuildMissionRewardsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
