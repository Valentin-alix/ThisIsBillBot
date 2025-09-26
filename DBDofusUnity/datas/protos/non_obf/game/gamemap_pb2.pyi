import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MapChangeRequest(_message.Message):
    __slots__ = ("map_id", "auto_pilot")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    AUTO_PILOT_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    auto_pilot: bool
    def __init__(self, map_id: _Optional[int] = ..., auto_pilot: bool = ...) -> None: ...

class GameRolePlayShowActorsEvent(_message.Message):
    __slots__ = ("actors",)
    ACTORS_FIELD_NUMBER: _ClassVar[int]
    actors: _containers.RepeatedCompositeFieldContainer[_common_pb2.ActorPositionInformation]
    def __init__(self, actors: _Optional[_Iterable[_Union[_common_pb2.ActorPositionInformation, _Mapping]]] = ...) -> None: ...

class MapMovementRefusedEvent(_message.Message):
    __slots__ = ("cell_x", "cell_y")
    CELL_X_FIELD_NUMBER: _ClassVar[int]
    CELL_Y_FIELD_NUMBER: _ClassVar[int]
    cell_x: int
    cell_y: int
    def __init__(self, cell_x: _Optional[int] = ..., cell_y: _Optional[int] = ...) -> None: ...

class MapComplementaryInformationEvent(_message.Message):
    __slots__ = ("subarea_id", "map_id", "houses", "actors", "interactive_elements", "stated_elements", "obstacles", "fights", "has_aggressive_monsters", "unknown_four_hundred_seven", "in_house_information", "coordinates", "breach_information", "anomaly_information", "haven_bag_information")
    SUBAREA_ID_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    HOUSES_FIELD_NUMBER: _ClassVar[int]
    ACTORS_FIELD_NUMBER: _ClassVar[int]
    INTERACTIVE_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    STATED_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    FIGHTS_FIELD_NUMBER: _ClassVar[int]
    HAS_AGGRESSIVE_MONSTERS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SEVEN_FIELD_NUMBER: _ClassVar[int]
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
    unknown_four_hundred_seven: _containers.RepeatedCompositeFieldContainer[UnknownTwoHundredOne]
    in_house_information: MapComplementaryInHouseInformation
    coordinates: _common_pb2.MapCoordinates
    breach_information: MapComplementaryBreachInformation
    anomaly_information: MapComplementaryAnomalyInformation
    haven_bag_information: MapComplementaryHavenBagInformation
    def __init__(self, subarea_id: _Optional[int] = ..., map_id: _Optional[int] = ..., houses: _Optional[_Iterable[_Union[_common_pb2.House, _Mapping]]] = ..., actors: _Optional[_Iterable[_Union[_common_pb2.ActorPositionInformation, _Mapping]]] = ..., interactive_elements: _Optional[_Iterable[_Union[_common_pb2.InteractiveElement, _Mapping]]] = ..., stated_elements: _Optional[_Iterable[_Union[_common_pb2.StatedElement, _Mapping]]] = ..., obstacles: _Optional[_Iterable[_Union[MapObstacle, _Mapping]]] = ..., fights: _Optional[_Iterable[_Union[_common_pb2.FightCommonInformation, _Mapping]]] = ..., has_aggressive_monsters: bool = ..., unknown_four_hundred_seven: _Optional[_Iterable[_Union[UnknownTwoHundredOne, _Mapping]]] = ..., in_house_information: _Optional[_Union[MapComplementaryInHouseInformation, _Mapping]] = ..., coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., breach_information: _Optional[_Union[MapComplementaryBreachInformation, _Mapping]] = ..., anomaly_information: _Optional[_Union[MapComplementaryAnomalyInformation, _Mapping]] = ..., haven_bag_information: _Optional[_Union[MapComplementaryHavenBagInformation, _Mapping]] = ...) -> None: ...

class MapFightCountEvent(_message.Message):
    __slots__ = ("fight_count",)
    FIGHT_COUNT_FIELD_NUMBER: _ClassVar[int]
    fight_count: int
    def __init__(self, fight_count: _Optional[int] = ...) -> None: ...

class MapMovementRequest(_message.Message):
    __slots__ = ("key_cells", "map_id", "cautious")
    KEY_CELLS_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    CAUTIOUS_FIELD_NUMBER: _ClassVar[int]
    key_cells: _containers.RepeatedScalarFieldContainer[int]
    map_id: int
    cautious: bool
    def __init__(self, key_cells: _Optional[_Iterable[int]] = ..., map_id: _Optional[int] = ..., cautious: bool = ...) -> None: ...

class MapComplementaryWithCoordsInformation(_message.Message):
    __slots__ = ("coordinates",)
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    coordinates: _common_pb2.MapCoordinates
    def __init__(self, coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ...) -> None: ...

class MapMovementConfirmResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

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

class MapCurrentInstanceEvent(_message.Message):
    __slots__ = ("map_id", "instantiate_map_id")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANTIATE_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    instantiate_map_id: int
    def __init__(self, map_id: _Optional[int] = ..., instantiate_map_id: _Optional[int] = ...) -> None: ...

class MapComplementaryInHouseInformation(_message.Message):
    __slots__ = ("current_house",)
    CURRENT_HOUSE_FIELD_NUMBER: _ClassVar[int]
    current_house: _common_pb2.House
    def __init__(self, current_house: _Optional[_Union[_common_pb2.House, _Mapping]] = ...) -> None: ...

class MapMovementCancelRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    def __init__(self, cell_id: _Optional[int] = ...) -> None: ...

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

class MapChangeOrientationRequest(_message.Message):
    __slots__ = ("direction",)
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    direction: _common_pb2.Direction
    def __init__(self, direction: _Optional[_Union[_common_pb2.Direction, str]] = ...) -> None: ...

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

class MapRunningFightDetailsEvent(_message.Message):
    __slots__ = ("fight_id", "attackers", "defenders")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    ATTACKERS_FIELD_NUMBER: _ClassVar[int]
    DEFENDERS_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    attackers: _containers.RepeatedCompositeFieldContainer[_common_pb2.FighterLightInformation]
    defenders: _containers.RepeatedCompositeFieldContainer[_common_pb2.FighterLightInformation]
    def __init__(self, fight_id: _Optional[int] = ..., attackers: _Optional[_Iterable[_Union[_common_pb2.FighterLightInformation, _Mapping]]] = ..., defenders: _Optional[_Iterable[_Union[_common_pb2.FighterLightInformation, _Mapping]]] = ...) -> None: ...

class MapTeleportOnSameEvent(_message.Message):
    __slots__ = ("player_id", "cell_id")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    cell_id: int
    def __init__(self, player_id: _Optional[int] = ..., cell_id: _Optional[int] = ...) -> None: ...

class MapMovementConfirmRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MapRunningFightStopListeningRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MapRunningFightsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MapComplementaryBreachInformation(_message.Message):
    __slots__ = ("unknown_four_hundred_four", "unknown_four_hundred_five", "unknown_four_hundred_six")
    UNKNOWN_FOUR_HUNDRED_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_four: BreachBranchesInformation
    unknown_four_hundred_five: BreachRoomInformation
    unknown_four_hundred_six: UnknownTwoHundred
    def __init__(self, unknown_four_hundred_four: _Optional[_Union[BreachBranchesInformation, _Mapping]] = ..., unknown_four_hundred_five: _Optional[_Union[BreachRoomInformation, _Mapping]] = ..., unknown_four_hundred_six: _Optional[_Union[UnknownTwoHundred, _Mapping]] = ...) -> None: ...

class MapObstacleUpdateEvent(_message.Message):
    __slots__ = ("obstacles",)
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    obstacles: _containers.RepeatedCompositeFieldContainer[MapObstacle]
    def __init__(self, obstacles: _Optional[_Iterable[_Union[MapObstacle, _Mapping]]] = ...) -> None: ...

class MapCurrentEvent(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

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

class MapInformationRequest(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

class MapChangeOrientationEvent(_message.Message):
    __slots__ = ("actor_id", "direction")
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    direction: _common_pb2.Direction
    def __init__(self, actor_id: _Optional[int] = ..., direction: _Optional[_Union[_common_pb2.Direction, str]] = ...) -> None: ...

class MapRunningFightsEvent(_message.Message):
    __slots__ = ("fights",)
    FIGHTS_FIELD_NUMBER: _ClassVar[int]
    fights: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightExternalInformation]
    def __init__(self, fights: _Optional[_Iterable[_Union[_common_pb2.FightExternalInformation, _Mapping]]] = ...) -> None: ...

class MapMovementEvent(_message.Message):
    __slots__ = ("cells", "character_id", "cautious", "direction")
    CELLS_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CAUTIOUS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedScalarFieldContainer[int]
    character_id: int
    cautious: bool
    direction: int
    def __init__(self, cells: _Optional[_Iterable[int]] = ..., character_id: _Optional[int] = ..., cautious: bool = ..., direction: _Optional[int] = ...) -> None: ...

class MapComplementaryAnomalyInformation(_message.Message):
    __slots__ = ("level", "closing_time")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    CLOSING_TIME_FIELD_NUMBER: _ClassVar[int]
    level: int
    closing_time: int
    def __init__(self, level: _Optional[int] = ..., closing_time: _Optional[int] = ...) -> None: ...

class MapRunningFightDetailsRequest(_message.Message):
    __slots__ = ("fight_id", "unknown_four_hundred_eight")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_EIGHT_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    unknown_four_hundred_eight: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fight_id: _Optional[int] = ..., unknown_four_hundred_eight: _Optional[_Iterable[str]] = ...) -> None: ...

class MapErrorNotFoundRequest(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

class UnknownOneHundredNinetyNine(_message.Message):
    __slots__ = ("unknown_four_hundred_twenty_one",)
    UNKNOWN_FOUR_HUNDRED_TWENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_twenty_one: int
    def __init__(self, unknown_four_hundred_twenty_one: _Optional[int] = ...) -> None: ...

class UnknownTwoHundred(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownTwoHundredOne(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachBranchesInformation(_message.Message):
    __slots__ = ("unknown_four_hundred",)
    class Branch(_message.Message):
        __slots__ = ("unknown_three_hundred_ninety_eight", "unknown_three_hundred_ninety_nine")
        UNKNOWN_THREE_HUNDRED_NINETY_EIGHT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THREE_HUNDRED_NINETY_NINE_FIELD_NUMBER: _ClassVar[int]
        unknown_three_hundred_ninety_eight: int
        unknown_three_hundred_ninety_nine: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_three_hundred_ninety_eight: _Optional[int] = ..., unknown_three_hundred_ninety_nine: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FOUR_HUNDRED_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred: BreachBranchesInformation.Branch
    def __init__(self, unknown_four_hundred: _Optional[_Union[BreachBranchesInformation.Branch, _Mapping]] = ...) -> None: ...

class BreachRoomInformation(_message.Message):
    __slots__ = ("unknown_four_hundred_one", "unknown_four_hundred_two", "unknown_four_hundred_three")
    UNKNOWN_FOUR_HUNDRED_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_THREE_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_one: int
    unknown_four_hundred_two: int
    unknown_four_hundred_three: int
    def __init__(self, unknown_four_hundred_one: _Optional[int] = ..., unknown_four_hundred_two: _Optional[int] = ..., unknown_four_hundred_three: _Optional[int] = ...) -> None: ...

class UnknownTwoHundredTwo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownOneHundredNinetyEight(_message.Message):
    __slots__ = ("unknown_four_hundred_sixteen", "unknown_four_hundred_seventeen", "unknown_four_hundred_eighteen", "unknown_four_hundred_nineteen", "unknown_four_hundred_twenty")
    UNKNOWN_FOUR_HUNDRED_SIXTEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SEVENTEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_EIGHTEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_NINETEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_TWENTY_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_sixteen: int
    unknown_four_hundred_seventeen: int
    unknown_four_hundred_eighteen: int
    unknown_four_hundred_nineteen: int
    unknown_four_hundred_twenty: int
    def __init__(self, unknown_four_hundred_sixteen: _Optional[int] = ..., unknown_four_hundred_seventeen: _Optional[int] = ..., unknown_four_hundred_eighteen: _Optional[int] = ..., unknown_four_hundred_nineteen: _Optional[int] = ..., unknown_four_hundred_twenty: _Optional[int] = ...) -> None: ...

class UnknownOneHundredNinetyFour(_message.Message):
    __slots__ = ("unknown_four_hundred_ten", "unknown_four_hundred_eleven", "unknown_four_hundred_twelve")
    class UnknownOneHundredNinetyFive(_message.Message):
        __slots__ = ("unknown_four_hundred_nine",)
        UNKNOWN_FOUR_HUNDRED_NINE_FIELD_NUMBER: _ClassVar[int]
        unknown_four_hundred_nine: UnknownOneHundredNinetyEight
        def __init__(self, unknown_four_hundred_nine: _Optional[_Union[UnknownOneHundredNinetyEight, _Mapping]] = ...) -> None: ...
    UNKNOWN_FOUR_HUNDRED_TEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_ELEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_TWELVE_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_ten: int
    unknown_four_hundred_eleven: UnknownOneHundredNinetyFour.UnknownOneHundredNinetyFive
    unknown_four_hundred_twelve: int
    def __init__(self, unknown_four_hundred_ten: _Optional[int] = ..., unknown_four_hundred_eleven: _Optional[_Union[UnknownOneHundredNinetyFour.UnknownOneHundredNinetyFive, _Mapping]] = ..., unknown_four_hundred_twelve: _Optional[int] = ...) -> None: ...

class UnknownOneHundredNinetySix(_message.Message):
    __slots__ = ("unknown_four_hundred_fourteen", "unknown_four_hundred_fifteen")
    class UnknownOneHundredNinetySeven(_message.Message):
        __slots__ = ("unknown_four_hundred_thirteen",)
        UNKNOWN_FOUR_HUNDRED_THIRTEEN_FIELD_NUMBER: _ClassVar[int]
        unknown_four_hundred_thirteen: UnknownOneHundredNinetyEight
        def __init__(self, unknown_four_hundred_thirteen: _Optional[_Union[UnknownOneHundredNinetyEight, _Mapping]] = ...) -> None: ...
    UNKNOWN_FOUR_HUNDRED_FOURTEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_FIFTEEN_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_fourteen: UnknownOneHundredNinetySix.UnknownOneHundredNinetySeven
    unknown_four_hundred_fifteen: int
    def __init__(self, unknown_four_hundred_fourteen: _Optional[_Union[UnknownOneHundredNinetySix.UnknownOneHundredNinetySeven, _Mapping]] = ..., unknown_four_hundred_fifteen: _Optional[int] = ...) -> None: ...
