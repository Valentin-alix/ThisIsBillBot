import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SmileyRequest(_message.Message):
    __slots__ = ("smiley_id",)
    SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
    smiley_id: int
    def __init__(self, smiley_id: _Optional[int] = ...) -> None: ...

class SmileyEvent(_message.Message):
    __slots__ = ("entity_id", "smiley_id", "account_id", "cell_id")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    smiley_id: int
    account_id: int
    cell_id: int
    def __init__(self, entity_id: _Optional[int] = ..., smiley_id: _Optional[int] = ..., account_id: _Optional[int] = ..., cell_id: _Optional[int] = ...) -> None: ...

class AdditionalSmileyEvent(_message.Message):
    __slots__ = ("pack_id",)
    PACK_ID_FIELD_NUMBER: _ClassVar[int]
    pack_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, pack_id: _Optional[_Iterable[int]] = ...) -> None: ...

class SetMoodRequest(_message.Message):
    __slots__ = ("smiley_id",)
    SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
    smiley_id: int
    def __init__(self, smiley_id: _Optional[int] = ...) -> None: ...

class SetMoodEvent(_message.Message):
    __slots__ = ("result", "smiley_id")
    class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[SetMoodEvent.Result]
        ERROR_UNKNOWN: _ClassVar[SetMoodEvent.Result]
        ERROR_FLOOD: _ClassVar[SetMoodEvent.Result]
    OK: SetMoodEvent.Result
    ERROR_UNKNOWN: SetMoodEvent.Result
    ERROR_FLOOD: SetMoodEvent.Result
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
    result: SetMoodEvent.Result
    smiley_id: int
    def __init__(self, result: _Optional[_Union[SetMoodEvent.Result, str]] = ..., smiley_id: _Optional[int] = ...) -> None: ...

class MoodUpdateEvent(_message.Message):
    __slots__ = ("account_id", "character_id", "smiley_id")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    character_id: int
    smiley_id: int
    def __init__(self, account_id: _Optional[int] = ..., character_id: _Optional[int] = ..., smiley_id: _Optional[int] = ...) -> None: ...

class SpouseStatusEvent(_message.Message):
    __slots__ = ("has_spouse",)
    HAS_SPOUSE_FIELD_NUMBER: _ClassVar[int]
    has_spouse: bool
    def __init__(self, has_spouse: bool = ...) -> None: ...

class SpouseInformationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SpouseInformationEvent(_message.Message):
    __slots__ = ("account_id", "character_id", "character_name", "character_level", "breed_id", "gender", "guild", "alliance", "alignment", "entity_look", "online")
    class Online(_message.Message):
        __slots__ = ("map_id", "sub_area_id", "area_id", "in_fight", "following")
        MAP_ID_FIELD_NUMBER: _ClassVar[int]
        SUB_AREA_ID_FIELD_NUMBER: _ClassVar[int]
        AREA_ID_FIELD_NUMBER: _ClassVar[int]
        IN_FIGHT_FIELD_NUMBER: _ClassVar[int]
        FOLLOWING_FIELD_NUMBER: _ClassVar[int]
        map_id: int
        sub_area_id: int
        area_id: int
        in_fight: bool
        following: bool
        def __init__(self, map_id: _Optional[int] = ..., sub_area_id: _Optional[int] = ..., area_id: _Optional[int] = ..., in_fight: bool = ..., following: bool = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_NAME_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_LEVEL_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    GUILD_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_FIELD_NUMBER: _ClassVar[int]
    ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    ENTITY_LOOK_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    character_id: int
    character_name: str
    character_level: int
    breed_id: int
    gender: _common_pb2.Gender
    guild: _common_pb2.GuildInformation
    alliance: _common_pb2.AllianceInformation
    alignment: _common_pb2.Alignment
    entity_look: _common_pb2.EntityLook
    online: SpouseInformationEvent.Online
    def __init__(self, account_id: _Optional[int] = ..., character_id: _Optional[int] = ..., character_name: _Optional[str] = ..., character_level: _Optional[int] = ..., breed_id: _Optional[int] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ..., guild: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., alliance: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., alignment: _Optional[_Union[_common_pb2.Alignment, str]] = ..., entity_look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., online: _Optional[_Union[SpouseInformationEvent.Online, _Mapping]] = ...) -> None: ...

class JoinFriendRequest(_message.Message):
    __slots__ = ("actor_id",)
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    def __init__(self, actor_id: _Optional[int] = ...) -> None: ...

class JoinSpouseRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SubscribeSpouseCompassRequest(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class DiceRollRequest(_message.Message):
    __slots__ = ("dice", "faces")
    DICE_FIELD_NUMBER: _ClassVar[int]
    FACES_FIELD_NUMBER: _ClassVar[int]
    dice: int
    faces: int
    def __init__(self, dice: _Optional[int] = ..., faces: _Optional[int] = ...) -> None: ...

class PvpEnableSetRequest(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class PlayersMapAttackableStatusUpdateEvent(_message.Message):
    __slots__ = ("pvp_players",)
    class AttackableStatus(_message.Message):
        __slots__ = ("character_id", "status", "koth_role", "picto_score")
        CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        KOTH_ROLE_FIELD_NUMBER: _ClassVar[int]
        PICTO_SCORE_FIELD_NUMBER: _ClassVar[int]
        character_id: int
        status: _common_pb2.AttackableStatus
        koth_role: int
        picto_score: int
        def __init__(self, character_id: _Optional[int] = ..., status: _Optional[_Union[_common_pb2.AttackableStatus, str]] = ..., koth_role: _Optional[int] = ..., picto_score: _Optional[int] = ...) -> None: ...
    PVP_PLAYERS_FIELD_NUMBER: _ClassVar[int]
    pvp_players: _containers.RepeatedCompositeFieldContainer[PlayersMapAttackableStatusUpdateEvent.AttackableStatus]
    def __init__(self, pvp_players: _Optional[_Iterable[_Union[PlayersMapAttackableStatusUpdateEvent.AttackableStatus, _Mapping]]] = ...) -> None: ...

class SelfAttackableStatusUpdateEvent(_message.Message):
    __slots__ = ("status", "probation_time", "koth_role", "picto_score")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROBATION_TIME_FIELD_NUMBER: _ClassVar[int]
    KOTH_ROLE_FIELD_NUMBER: _ClassVar[int]
    PICTO_SCORE_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.AttackableStatus
    probation_time: int
    koth_role: int
    picto_score: int
    def __init__(self, status: _Optional[_Union[_common_pb2.AttackableStatus, str]] = ..., probation_time: _Optional[int] = ..., koth_role: _Optional[int] = ..., picto_score: _Optional[int] = ...) -> None: ...

class AlignmentRankUpdateEvent(_message.Message):
    __slots__ = ("alignment_rank", "verbose")
    ALIGNMENT_RANK_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    alignment_rank: int
    verbose: bool
    def __init__(self, alignment_rank: _Optional[int] = ..., verbose: bool = ...) -> None: ...
