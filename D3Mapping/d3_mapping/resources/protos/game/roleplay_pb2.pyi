import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlayerFightRequest(_message.Message):
    __slots__ = ("target_id", "target_cell_id", "friendly")
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    FRIENDLY_FIELD_NUMBER: _ClassVar[int]
    target_id: int
    target_cell_id: int
    friendly: bool
    def __init__(self, target_id: _Optional[int] = ..., target_cell_id: _Optional[int] = ..., friendly: bool = ...) -> None: ...

class PlayerFightFriendlyAnswerRequest(_message.Message):
    __slots__ = ("fight_id", "accept")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    accept: bool
    def __init__(self, fight_id: _Optional[int] = ..., accept: bool = ...) -> None: ...

class AttackMonsterRequest(_message.Message):
    __slots__ = ("monster_group_id",)
    MONSTER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    monster_group_id: int
    def __init__(self, monster_group_id: _Optional[int] = ...) -> None: ...

class ExitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DelayedActionCancelRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FightRequestCanceledEvent(_message.Message):
    __slots__ = ("fight_id", "source_id", "target_id")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    source_id: int
    target_id: int
    def __init__(self, fight_id: _Optional[int] = ..., source_id: _Optional[int] = ..., target_id: _Optional[int] = ...) -> None: ...

class AggressionEvent(_message.Message):
    __slots__ = ("attacker_id", "defender_id")
    ATTACKER_ID_FIELD_NUMBER: _ClassVar[int]
    DEFENDER_ID_FIELD_NUMBER: _ClassVar[int]
    attacker_id: int
    defender_id: int
    def __init__(self, attacker_id: _Optional[int] = ..., defender_id: _Optional[int] = ...) -> None: ...

class PlayerFightFriendlyRequestedEvent(_message.Message):
    __slots__ = ("fight_id", "source_id", "target_id")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    source_id: int
    target_id: int
    def __init__(self, fight_id: _Optional[int] = ..., source_id: _Optional[int] = ..., target_id: _Optional[int] = ...) -> None: ...

class PlayerFightFriendlyAnsweredEvent(_message.Message):
    __slots__ = ("fight_id", "source_id", "target_id", "accept")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    source_id: int
    target_id: int
    accept: bool
    def __init__(self, fight_id: _Optional[int] = ..., source_id: _Optional[int] = ..., target_id: _Optional[int] = ..., accept: bool = ...) -> None: ...

class MonsterAngryAtPlayerEvent(_message.Message):
    __slots__ = ("character_id", "monster_group_id", "angry_start_time", "attack_time")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    MONSTER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ANGRY_START_TIME_FIELD_NUMBER: _ClassVar[int]
    ATTACK_TIME_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    monster_group_id: int
    angry_start_time: int
    attack_time: int
    def __init__(self, character_id: _Optional[int] = ..., monster_group_id: _Optional[int] = ..., angry_start_time: _Optional[int] = ..., attack_time: _Optional[int] = ...) -> None: ...

class MonsterNotAngryAtPlayerEvent(_message.Message):
    __slots__ = ("character_id", "monster_group_id")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    MONSTER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    monster_group_id: int
    def __init__(self, character_id: _Optional[int] = ..., monster_group_id: _Optional[int] = ...) -> None: ...

class ShowChallengeEvent(_message.Message):
    __slots__ = ("fight_information",)
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.FightCommonInformation
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.FightCommonInformation, _Mapping]] = ...) -> None: ...

class RemoveChallengeEvent(_message.Message):
    __slots__ = ("fight_id",)
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    def __init__(self, fight_id: _Optional[int] = ...) -> None: ...

class SpellAnimEvent(_message.Message):
    __slots__ = ("caster_id", "target_cell_id", "spell_id", "spell_level", "direction")
    CASTER_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    SPELL_LEVEL_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    caster_id: int
    target_cell_id: int
    spell_id: int
    spell_level: int
    direction: _common_pb2.Direction
    def __init__(self, caster_id: _Optional[int] = ..., target_cell_id: _Optional[int] = ..., spell_id: _Optional[int] = ..., spell_level: _Optional[int] = ..., direction: _Optional[_Union[_common_pb2.Direction, str]] = ...) -> None: ...

class DelayedActionEvent(_message.Message):
    __slots__ = ("character_id", "delayed_action_type", "delayed_end_time", "object_gid")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    DELAYED_ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    DELAYED_END_TIME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    delayed_action_type: _common_pb2.DelayedActionType
    delayed_end_time: int
    object_gid: int
    def __init__(self, character_id: _Optional[int] = ..., delayed_action_type: _Optional[_Union[_common_pb2.DelayedActionType, str]] = ..., delayed_end_time: _Optional[int] = ..., object_gid: _Optional[int] = ...) -> None: ...

class DelayedActionFinishedEvent(_message.Message):
    __slots__ = ("character_id", "delayed_action_type")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    DELAYED_ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    delayed_action_type: _common_pb2.DelayedActionType
    def __init__(self, character_id: _Optional[int] = ..., delayed_action_type: _Optional[_Union[_common_pb2.DelayedActionType, str]] = ...) -> None: ...
