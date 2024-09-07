from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MapMovementRequest(_message.Message):
    __slots__ = ("key_cells", "map_id", "cautious")
    KEY_CELLS_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    CAUTIOUS_FIELD_NUMBER: _ClassVar[int]
    key_cells: _containers.RepeatedScalarFieldContainer[int]
    map_id: int
    cautious: bool
    def __init__(self, key_cells: _Optional[_Iterable[int]] = ..., map_id: _Optional[int] = ..., cautious: bool = ...) -> None: ...

class MapMovementCancelRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    def __init__(self, cell_id: _Optional[int] = ...) -> None: ...

class MapMovementConfirmRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MapChangeOrientationRequest(_message.Message):
    __slots__ = ("direction",)
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    direction: _common_pb2.Direction
    def __init__(self, direction: _Optional[_Union[_common_pb2.Direction, str]] = ...) -> None: ...

class MapErrorNotFoundRequest(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

class MapChangeRequest(_message.Message):
    __slots__ = ("map_id", "auto_pilot")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    AUTO_PILOT_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    auto_pilot: bool
    def __init__(self, map_id: _Optional[int] = ..., auto_pilot: bool = ...) -> None: ...

class MapRunningFightsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MapRunningFightStopListeningRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MapRunningFightDetailsRequest(_message.Message):
    __slots__ = ("fight_id",)
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    def __init__(self, fight_id: _Optional[int] = ...) -> None: ...

class MapInformationRequest(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

class MapMovementRefusedEvent(_message.Message):
    __slots__ = ("cell_x", "cell_y")
    CELL_X_FIELD_NUMBER: _ClassVar[int]
    CELL_Y_FIELD_NUMBER: _ClassVar[int]
    cell_x: int
    cell_y: int
    def __init__(self, cell_x: _Optional[int] = ..., cell_y: _Optional[int] = ...) -> None: ...

class MapMovementEvent(_message.Message):
    __slots__ = ("cells", "direction", "character_id", "cautious")
    CELLS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CAUTIOUS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedScalarFieldContainer[int]
    direction: int
    character_id: int
    cautious: bool
    def __init__(self, cells: _Optional[_Iterable[int]] = ..., direction: _Optional[int] = ..., character_id: _Optional[int] = ..., cautious: bool = ...) -> None: ...

class MapChangeOrientationEvent(_message.Message):
    __slots__ = ("actor_id", "direction")
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    direction: _common_pb2.Direction
    def __init__(self, actor_id: _Optional[int] = ..., direction: _Optional[_Union[_common_pb2.Direction, str]] = ...) -> None: ...

class MapCurrentEvent(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

class MapCurrentInstanceEvent(_message.Message):
    __slots__ = ("map_id", "instantiate_map_id")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANTIATE_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    instantiate_map_id: int
    def __init__(self, map_id: _Optional[int] = ..., instantiate_map_id: _Optional[int] = ...) -> None: ...

class MapTeleportOnSameEvent(_message.Message):
    __slots__ = ("player_id", "cell_id")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    cell_id: int
    def __init__(self, player_id: _Optional[int] = ..., cell_id: _Optional[int] = ...) -> None: ...

class MapFightCountEvent(_message.Message):
    __slots__ = ("fight_count",)
    FIGHT_COUNT_FIELD_NUMBER: _ClassVar[int]
    fight_count: int
    def __init__(self, fight_count: _Optional[int] = ...) -> None: ...

class MapRunningFightsEvent(_message.Message):
    __slots__ = ("fights",)
    FIGHTS_FIELD_NUMBER: _ClassVar[int]
    fights: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightExternalInformation]
    def __init__(self, fights: _Optional[_Iterable[_Union[_common_pb2.FightExternalInformation, _Mapping]]] = ...) -> None: ...

class MapRunningFightDetailsEvent(_message.Message):
    __slots__ = ("fight_id", "attackers", "defenders")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    ATTACKERS_FIELD_NUMBER: _ClassVar[int]
    DEFENDERS_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    attackers: _containers.RepeatedCompositeFieldContainer[_common_pb2.FighterLightInformation]
    defenders: _containers.RepeatedCompositeFieldContainer[_common_pb2.FighterLightInformation]
    def __init__(self, fight_id: _Optional[int] = ..., attackers: _Optional[_Iterable[_Union[_common_pb2.FighterLightInformation, _Mapping]]] = ..., defenders: _Optional[_Iterable[_Union[_common_pb2.FighterLightInformation, _Mapping]]] = ...) -> None: ...

class MapRunningFightDetailsExtendedEvent(_message.Message):
    __slots__ = ("fight_id", "attackers", "defenders", "named_party_teams")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    ATTACKERS_FIELD_NUMBER: _ClassVar[int]
    DEFENDERS_FIELD_NUMBER: _ClassVar[int]
    NAMED_PARTY_TEAMS_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    attackers: _containers.RepeatedCompositeFieldContainer[_common_pb2.FighterLightInformation]
    defenders: _containers.RepeatedCompositeFieldContainer[_common_pb2.FighterLightInformation]
    named_party_teams: _containers.RepeatedCompositeFieldContainer[_common_pb2.NamedPartyTeam]
    def __init__(self, fight_id: _Optional[int] = ..., attackers: _Optional[_Iterable[_Union[_common_pb2.FighterLightInformation, _Mapping]]] = ..., defenders: _Optional[_Iterable[_Union[_common_pb2.FighterLightInformation, _Mapping]]] = ..., named_party_teams: _Optional[_Iterable[_Union[_common_pb2.NamedPartyTeam, _Mapping]]] = ...) -> None: ...

class MapObstacleUpdateEvent(_message.Message):
    __slots__ = ("obstacles",)
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    obstacles: _containers.RepeatedCompositeFieldContainer[MapObstacle]
    def __init__(self, obstacles: _Optional[_Iterable[_Union[MapObstacle, _Mapping]]] = ...) -> None: ...

class MapComplementaryInformationEvent(_message.Message):
    __slots__ = ("subarea_id", "map_id", "houses", "actors", "interactive_elements", "stated_elements", "obstacles", "fights", "has_aggressive_monsters", "in_house_information", "coordinates", "breach_information", "anomaly_information", "haven_bag_information")
    SUBAREA_ID_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    HOUSES_FIELD_NUMBER: _ClassVar[int]
    ACTORS_FIELD_NUMBER: _ClassVar[int]
    INTERACTIVE_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    STATED_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    FIGHTS_FIELD_NUMBER: _ClassVar[int]
    HAS_AGGRESSIVE_MONSTERS_FIELD_NUMBER: _ClassVar[int]
    IN_HOUSE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    BREACH_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    ANOMALY_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    HAVEN_BAG_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    subarea_id: int
    map_id: int
    houses: _containers.RepeatedCompositeFieldContainer[_common_pb2.House]
    actors: _containers.RepeatedCompositeFieldContainer[_common_pb2.ActorPositionInformation]
    interactive_elements: _containers.RepeatedCompositeFieldContainer[_common_pb2.InteractiveElement]
    stated_elements: _containers.RepeatedCompositeFieldContainer[_common_pb2.StatedElement]
    obstacles: _containers.RepeatedCompositeFieldContainer[MapObstacle]
    fights: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightCommonInformation]
    has_aggressive_monsters: bool
    in_house_information: MapComplementaryInHouseInformation
    coordinates: _common_pb2.MapCoordinates
    breach_information: MapComplementaryBreachInformation
    anomaly_information: MapComplementaryAnomalyInformation
    haven_bag_information: MapComplementaryHavenBagInformation
    def __init__(self, subarea_id: _Optional[int] = ..., map_id: _Optional[int] = ..., houses: _Optional[_Iterable[_Union[_common_pb2.House, _Mapping]]] = ..., actors: _Optional[_Iterable[_Union[_common_pb2.ActorPositionInformation, _Mapping]]] = ..., interactive_elements: _Optional[_Iterable[_Union[_common_pb2.InteractiveElement, _Mapping]]] = ..., stated_elements: _Optional[_Iterable[_Union[_common_pb2.StatedElement, _Mapping]]] = ..., obstacles: _Optional[_Iterable[_Union[MapObstacle, _Mapping]]] = ..., fights: _Optional[_Iterable[_Union[_common_pb2.FightCommonInformation, _Mapping]]] = ..., has_aggressive_monsters: bool = ..., in_house_information: _Optional[_Union[MapComplementaryInHouseInformation, _Mapping]] = ..., coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., breach_information: _Optional[_Union[MapComplementaryBreachInformation, _Mapping]] = ..., anomaly_information: _Optional[_Union[MapComplementaryAnomalyInformation, _Mapping]] = ..., haven_bag_information: _Optional[_Union[MapComplementaryHavenBagInformation, _Mapping]] = ...) -> None: ...

class GameRolePlayShowActorsEvent(_message.Message):
    __slots__ = ("actors",)
    ACTORS_FIELD_NUMBER: _ClassVar[int]
    actors: _containers.RepeatedCompositeFieldContainer[_common_pb2.ActorPositionInformation]
    def __init__(self, actors: _Optional[_Iterable[_Union[_common_pb2.ActorPositionInformation, _Mapping]]] = ...) -> None: ...

class FightMapInformationEvent(_message.Message):
    __slots__ = ("subarea_id", "map_id", "coordinates", "breach_information", "anomaly_information")
    SUBAREA_ID_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    BREACH_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    ANOMALY_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    subarea_id: int
    map_id: int
    coordinates: _common_pb2.MapCoordinates
    breach_information: MapComplementaryBreachInformation
    anomaly_information: MapComplementaryAnomalyInformation
    def __init__(self, subarea_id: _Optional[int] = ..., map_id: _Optional[int] = ..., coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., breach_information: _Optional[_Union[MapComplementaryBreachInformation, _Mapping]] = ..., anomaly_information: _Optional[_Union[MapComplementaryAnomalyInformation, _Mapping]] = ...) -> None: ...

class MapComplementaryInHouseInformation(_message.Message):
    __slots__ = ("current_house",)
    CURRENT_HOUSE_FIELD_NUMBER: _ClassVar[int]
    current_house: _common_pb2.House
    def __init__(self, current_house: _Optional[_Union[_common_pb2.House, _Mapping]] = ...) -> None: ...

class MapComplementaryWithCoordsInformation(_message.Message):
    __slots__ = ("coordinates",)
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    coordinates: _common_pb2.MapCoordinates
    def __init__(self, coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ...) -> None: ...

class MapComplementaryBreachInformation(_message.Message):
    __slots__ = ("floor", "room", "infinity_mode", "branches")
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    INFINITY_MODE_FIELD_NUMBER: _ClassVar[int]
    BRANCHES_FIELD_NUMBER: _ClassVar[int]
    floor: int
    room: int
    infinity_mode: int
    branches: _containers.RepeatedCompositeFieldContainer[_common_pb2.BreachBranch]
    def __init__(self, floor: _Optional[int] = ..., room: _Optional[int] = ..., infinity_mode: _Optional[int] = ..., branches: _Optional[_Iterable[_Union[_common_pb2.BreachBranch, _Mapping]]] = ...) -> None: ...

class MapComplementaryAnomalyInformation(_message.Message):
    __slots__ = ("level", "closing_time")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    CLOSING_TIME_FIELD_NUMBER: _ClassVar[int]
    level: int
    closing_time: int
    def __init__(self, level: _Optional[int] = ..., closing_time: _Optional[int] = ...) -> None: ...

class MapComplementaryHavenBagInformation(_message.Message):
    __slots__ = ("owner_information", "theme", "room_id", "max_room_id")
    OWNER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    THEME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    owner_information: _common_pb2.Character
    theme: int
    room_id: int
    max_room_id: int
    def __init__(self, owner_information: _Optional[_Union[_common_pb2.Character, _Mapping]] = ..., theme: _Optional[int] = ..., room_id: _Optional[int] = ..., max_room_id: _Optional[int] = ...) -> None: ...

class MapObstacle(_message.Message):
    __slots__ = ("cell_id", "state")
    class ObstacleState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OBSTACLE_OPENED: _ClassVar[MapObstacle.ObstacleState]
        OBSTACLE_CLOSED: _ClassVar[MapObstacle.ObstacleState]
    OBSTACLE_OPENED: MapObstacle.ObstacleState
    OBSTACLE_CLOSED: MapObstacle.ObstacleState
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    state: MapObstacle.ObstacleState
    def __init__(self, cell_id: _Optional[int] = ..., state: _Optional[_Union[MapObstacle.ObstacleState, str]] = ...) -> None: ...
