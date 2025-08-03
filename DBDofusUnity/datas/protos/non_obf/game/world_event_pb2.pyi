import common_pb2 as _common_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownHeg(_message.Message):
    __slots__ = ("unknown_fllw", "unknown_flly", "unknown_fllz")
    UNKNOWN_FLLW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLLY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLLZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fllw: int
    unknown_flly: _containers.RepeatedScalarFieldContainer[int]
    unknown_fllz: str
    def __init__(self, unknown_fllw: _Optional[int] = ..., unknown_flly: _Optional[_Iterable[int]] = ..., unknown_fllz: _Optional[str] = ...) -> None: ...

class UnknownHeh(_message.Message):
    __slots__ = ("unknown_flmd", "award_type", "unknown_flmh", "player_name")
    UNKNOWN_FLMD_FIELD_NUMBER: _ClassVar[int]
    AWARD_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLMH_FIELD_NUMBER: _ClassVar[int]
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    unknown_flmd: int
    award_type: int
    unknown_flmh: int
    player_name: str
    def __init__(self, unknown_flmd: _Optional[int] = ..., award_type: _Optional[int] = ..., unknown_flmh: _Optional[int] = ..., player_name: _Optional[str] = ...) -> None: ...

class WorldEventOngoingListEvent(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[UnknownHeg]
    def __init__(self, events: _Optional[_Iterable[_Union[UnknownHeg, _Mapping]]] = ...) -> None: ...

class WorldEventDetailEvent(_message.Message):
    __slots__ = ("unknown_flpw", "unknown_flpx")
    class UnknownHfa(_message.Message):
        __slots__ = ("winner_count", "players", "unknown_flpm", "unknown_flpn")
        class UnknownFlpmValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FLPM_VALUE_UNSPECIFIED: _ClassVar[WorldEventDetailEvent.UnknownHfa.UnknownFlpmValue]
        UNKNOWN_FLPM_VALUE_UNSPECIFIED: WorldEventDetailEvent.UnknownHfa.UnknownFlpmValue
        WINNER_COUNT_FIELD_NUMBER: _ClassVar[int]
        PLAYERS_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FLPM_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FLPN_FIELD_NUMBER: _ClassVar[int]
        winner_count: int
        players: _containers.RepeatedCompositeFieldContainer[UnknownHfl]
        unknown_flpm: WorldEventDetailEvent.UnknownHfa.UnknownFlpmValue
        unknown_flpn: UnknownHfl
        def __init__(self, winner_count: _Optional[int] = ..., players: _Optional[_Iterable[_Union[UnknownHfl, _Mapping]]] = ..., unknown_flpm: _Optional[_Union[WorldEventDetailEvent.UnknownHfa.UnknownFlpmValue, str]] = ..., unknown_flpn: _Optional[_Union[UnknownHfl, _Mapping]] = ...) -> None: ...
    class UnknownHfb(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_FLPW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLPX_FIELD_NUMBER: _ClassVar[int]
    unknown_flpw: WorldEventDetailEvent.UnknownHfa
    unknown_flpx: WorldEventDetailEvent.UnknownHfb
    def __init__(self, unknown_flpw: _Optional[_Union[WorldEventDetailEvent.UnknownHfa, _Mapping]] = ..., unknown_flpx: _Optional[_Union[WorldEventDetailEvent.UnknownHfb, _Mapping]] = ...) -> None: ...

class UnknownHfl(_message.Message):
    __slots__ = ("rank", "score", "unknown_flrc", "player", "unknown_flre", "unknown_flrf")
    RANK_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLRC_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLRE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLRF_FIELD_NUMBER: _ClassVar[int]
    rank: int
    score: int
    unknown_flrc: UnknownHfh
    player: UnknownHeh
    unknown_flre: UnknownHfj
    unknown_flrf: UnknownHgb
    def __init__(self, rank: _Optional[int] = ..., score: _Optional[int] = ..., unknown_flrc: _Optional[_Union[UnknownHfh, _Mapping]] = ..., player: _Optional[_Union[UnknownHeh, _Mapping]] = ..., unknown_flre: _Optional[_Union[UnknownHfj, _Mapping]] = ..., unknown_flrf: _Optional[_Union[UnknownHgb, _Mapping]] = ...) -> None: ...

class UnknownHfh(_message.Message):
    __slots__ = ("unknown_flql",)
    UNKNOWN_FLQL_FIELD_NUMBER: _ClassVar[int]
    unknown_flql: int
    def __init__(self, unknown_flql: _Optional[int] = ...) -> None: ...

class UnknownHfj(_message.Message):
    __slots__ = ("unknown_flqv", "unknown_flqw")
    UNKNOWN_FLQV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLQW_FIELD_NUMBER: _ClassVar[int]
    unknown_flqv: _common_pb2.SocialEmblem
    unknown_flqw: str
    def __init__(self, unknown_flqv: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ..., unknown_flqw: _Optional[str] = ...) -> None: ...

class UnknownHgb(_message.Message):
    __slots__ = ("unknown_fltm", "unknown_fltn", "unknown_flto")
    UNKNOWN_FLTM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLTN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLTO_FIELD_NUMBER: _ClassVar[int]
    unknown_fltm: str
    unknown_fltn: int
    unknown_flto: _common_pb2.SocialEmblem
    def __init__(self, unknown_fltm: _Optional[str] = ..., unknown_fltn: _Optional[int] = ..., unknown_flto: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class WorldEventOccurrencesEvent(_message.Message):
    __slots__ = ("infos",)
    INFOS_FIELD_NUMBER: _ClassVar[int]
    infos: _containers.RepeatedCompositeFieldContainer[WorldEventOccurrence]
    def __init__(self, infos: _Optional[_Iterable[_Union[WorldEventOccurrence, _Mapping]]] = ...) -> None: ...

class UnknownHfi(_message.Message):
    __slots__ = ("unknown_flqp", "unknown_flqq")
    UNKNOWN_FLQP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLQQ_FIELD_NUMBER: _ClassVar[int]
    unknown_flqp: str
    unknown_flqq: int
    def __init__(self, unknown_flqp: _Optional[str] = ..., unknown_flqq: _Optional[int] = ...) -> None: ...

class UnknownHfo(_message.Message):
    __slots__ = ("unknown_flrm", "unknown_flrn")
    UNKNOWN_FLRM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FLRN_FIELD_NUMBER: _ClassVar[int]
    unknown_flrm: str
    unknown_flrn: str
    def __init__(self, unknown_flrm: _Optional[str] = ..., unknown_flrn: _Optional[str] = ...) -> None: ...

class WorldEventDetailRequest(_message.Message):
    __slots__ = ("event_uuid",)
    EVENT_UUID_FIELD_NUMBER: _ClassVar[int]
    event_uuid: str
    def __init__(self, event_uuid: _Optional[str] = ...) -> None: ...

class WorldEventTypeRequest(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: int
    def __init__(self, type: _Optional[int] = ...) -> None: ...

class WorldEventOccurrencesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WorldEventSelfOccurrencesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownHfr(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WorldEventOccurrence(_message.Message):
    __slots__ = ("done_date", "event_uuid", "type_id")
    DONE_DATE_FIELD_NUMBER: _ClassVar[int]
    EVENT_UUID_FIELD_NUMBER: _ClassVar[int]
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    done_date: str
    event_uuid: str
    type_id: int
    def __init__(self, done_date: _Optional[str] = ..., event_uuid: _Optional[str] = ..., type_id: _Optional[int] = ...) -> None: ...
