from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FightJoinRequest(_message.Message):
    __slots__ = ("fighter_id", "fight_id")
    FIGHTER_ID_FIELD_NUMBER: _ClassVar[int]
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    fighter_id: int
    fight_id: int
    def __init__(self, fighter_id: _Optional[int] = ..., fight_id: _Optional[int] = ...) -> None: ...

class FightSpectatePlayerRequest(_message.Message):
    __slots__ = ("player_id",)
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    def __init__(self, player_id: _Optional[int] = ...) -> None: ...

class FightPlacementPositionRequest(_message.Message):
    __slots__ = ("cell_id", "entity_id")
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    entity_id: int
    def __init__(self, cell_id: _Optional[int] = ..., entity_id: _Optional[int] = ...) -> None: ...

class FightPlacementSwapPositionsCancelRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    def __init__(self, request_id: _Optional[int] = ...) -> None: ...

class FightPlacementSwapPositionsAcceptRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    def __init__(self, request_id: _Optional[int] = ...) -> None: ...

class FightOptionToggleRequest(_message.Message):
    __slots__ = ("option",)
    OPTION_FIELD_NUMBER: _ClassVar[int]
    option: _common_pb2.FightOption
    def __init__(self, option: _Optional[_Union[_common_pb2.FightOption, str]] = ...) -> None: ...

class FightReadyRequest(_message.Message):
    __slots__ = ("is_ready",)
    IS_READY_FIELD_NUMBER: _ClassVar[int]
    is_ready: bool
    def __init__(self, is_ready: bool = ...) -> None: ...

class FightStartingEvent(_message.Message):
    __slots__ = ("fight_type", "fight_id", "attacker_id", "defender_id", "contain_boss", "monsters")
    FIGHT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    ATTACKER_ID_FIELD_NUMBER: _ClassVar[int]
    DEFENDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAIN_BOSS_FIELD_NUMBER: _ClassVar[int]
    MONSTERS_FIELD_NUMBER: _ClassVar[int]
    fight_type: _common_pb2.FightType
    fight_id: int
    attacker_id: int
    defender_id: int
    contain_boss: bool
    monsters: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, fight_type: _Optional[_Union[_common_pb2.FightType, str]] = ..., fight_id: _Optional[int] = ..., attacker_id: _Optional[int] = ..., defender_id: _Optional[int] = ..., contain_boss: bool = ..., monsters: _Optional[_Iterable[int]] = ...) -> None: ...

class FightJoinEvent(_message.Message):
    __slots__ = ("is_team_phase", "can_be_cancelled", "can_say_ready", "is_fight_started", "time_max_before_fight_start", "fight_type")
    IS_TEAM_PHASE_FIELD_NUMBER: _ClassVar[int]
    CAN_BE_CANCELLED_FIELD_NUMBER: _ClassVar[int]
    CAN_SAY_READY_FIELD_NUMBER: _ClassVar[int]
    IS_FIGHT_STARTED_FIELD_NUMBER: _ClassVar[int]
    TIME_MAX_BEFORE_FIGHT_START_FIELD_NUMBER: _ClassVar[int]
    FIGHT_TYPE_FIELD_NUMBER: _ClassVar[int]
    is_team_phase: bool
    can_be_cancelled: bool
    can_say_ready: bool
    is_fight_started: bool
    time_max_before_fight_start: int
    fight_type: _common_pb2.FightType
    def __init__(self, is_team_phase: bool = ..., can_be_cancelled: bool = ..., can_say_ready: bool = ..., is_fight_started: bool = ..., time_max_before_fight_start: _Optional[int] = ..., fight_type: _Optional[_Union[_common_pb2.FightType, str]] = ...) -> None: ...

class FightSpectatorJoinEvent(_message.Message):
    __slots__ = ("fight_join_event", "named_party_teams")
    FIGHT_JOIN_EVENT_FIELD_NUMBER: _ClassVar[int]
    NAMED_PARTY_TEAMS_FIELD_NUMBER: _ClassVar[int]
    fight_join_event: FightJoinEvent
    named_party_teams: _containers.RepeatedCompositeFieldContainer[_common_pb2.NamedPartyTeam]
    def __init__(self, fight_join_event: _Optional[_Union[FightJoinEvent, _Mapping]] = ..., named_party_teams: _Optional[_Iterable[_Union[_common_pb2.NamedPartyTeam, _Mapping]]] = ...) -> None: ...

class FightPlacementPossiblePositionsEvent(_message.Message):
    __slots__ = ("starting_positions", "team")
    STARTING_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    starting_positions: _common_pb2.FightStartingPositions
    team: _common_pb2.Team
    def __init__(self, starting_positions: _Optional[_Union[_common_pb2.FightStartingPositions, _Mapping]] = ..., team: _Optional[_Union[_common_pb2.Team, str]] = ...) -> None: ...

class FightPlacementSwapPositionsErrorEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FightPlacementSwapPositionsOfferEvent(_message.Message):
    __slots__ = ("request_id", "requester_id", "requester_cell_id", "target_id", "target_cell_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    requester_id: int
    requester_cell_id: int
    target_id: int
    target_cell_id: int
    def __init__(self, request_id: _Optional[int] = ..., requester_id: _Optional[int] = ..., requester_cell_id: _Optional[int] = ..., target_id: _Optional[int] = ..., target_cell_id: _Optional[int] = ...) -> None: ...

class FightPlacementSwapPositionsCancelledEvent(_message.Message):
    __slots__ = ("request_id", "canceller_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CANCELLER_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    canceller_id: int
    def __init__(self, request_id: _Optional[int] = ..., canceller_id: _Optional[int] = ...) -> None: ...

class FightPlacementSwapPositionsEvent(_message.Message):
    __slots__ = ("dispositions",)
    DISPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    dispositions: _containers.RepeatedCompositeFieldContainer[_common_pb2.EntityDisposition]
    def __init__(self, dispositions: _Optional[_Iterable[_Union[_common_pb2.EntityDisposition, _Mapping]]] = ...) -> None: ...

class FightOptionUpdateEvent(_message.Message):
    __slots__ = ("fight_id", "team", "option", "state")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    OPTION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    team: _common_pb2.Team
    option: _common_pb2.FightOption
    state: bool
    def __init__(self, fight_id: _Optional[int] = ..., team: _Optional[_Union[_common_pb2.Team, str]] = ..., option: _Optional[_Union[_common_pb2.FightOption, str]] = ..., state: bool = ...) -> None: ...

class FightTeamUpdateEvent(_message.Message):
    __slots__ = ("fight_id", "team")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    team: _common_pb2.FightTeamInformation
    def __init__(self, fight_id: _Optional[int] = ..., team: _Optional[_Union[_common_pb2.FightTeamInformation, _Mapping]] = ...) -> None: ...

class FightTeamRemoveMemberEvent(_message.Message):
    __slots__ = ("fight_id", "team", "character_id")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    team: _common_pb2.Team
    character_id: int
    def __init__(self, fight_id: _Optional[int] = ..., team: _Optional[_Union[_common_pb2.Team, str]] = ..., character_id: _Optional[int] = ...) -> None: ...

class FightHumanReadyStateEvent(_message.Message):
    __slots__ = ("character_id", "is_ready")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_READY_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    is_ready: bool
    def __init__(self, character_id: _Optional[int] = ..., is_ready: bool = ...) -> None: ...

class FightLeaveEvent(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class FightStartEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FightMapRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
