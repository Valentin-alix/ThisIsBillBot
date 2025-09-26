import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownFiveHundredFive(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFiveHundredSix(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFiveHundredSeven(_message.Message):
    __slots__ = ("award_type", "unknown_eight_hundred_sixty_seven", "player_name")
    AWARD_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SIXTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    award_type: int
    unknown_eight_hundred_sixty_seven: int
    player_name: str
    def __init__(self, award_type: _Optional[int] = ..., unknown_eight_hundred_sixty_seven: _Optional[int] = ..., player_name: _Optional[str] = ...) -> None: ...

class WorldEventOngoingListEvent(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[UnknownFiveHundredSix]
    def __init__(self, events: _Optional[_Iterable[_Union[UnknownFiveHundredSix, _Mapping]]] = ...) -> None: ...

class WorldEventDetailEvent(_message.Message):
    __slots__ = ("unknown_eight_hundred_eighty_two",)
    class UnknownFiveHundredFifteen(_message.Message):
        __slots__ = ("winner_count", "players", "unknown_eight_hundred_eighty_one")
        class UnknownFiveHundredSixteen(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FIVE_HUNDRED_SIXTEEN_UNSPECIFIED: _ClassVar[WorldEventDetailEvent.UnknownFiveHundredFifteen.UnknownFiveHundredSixteen]
        UNKNOWN_FIVE_HUNDRED_SIXTEEN_UNSPECIFIED: WorldEventDetailEvent.UnknownFiveHundredFifteen.UnknownFiveHundredSixteen
        WINNER_COUNT_FIELD_NUMBER: _ClassVar[int]
        PLAYERS_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_EIGHTY_ONE_FIELD_NUMBER: _ClassVar[int]
        winner_count: int
        players: _containers.RepeatedCompositeFieldContainer[UnknownFiveHundredEleven]
        unknown_eight_hundred_eighty_one: WorldEventDetailEvent.UnknownFiveHundredFifteen.UnknownFiveHundredSixteen
        def __init__(self, winner_count: _Optional[int] = ..., players: _Optional[_Iterable[_Union[UnknownFiveHundredEleven, _Mapping]]] = ..., unknown_eight_hundred_eighty_one: _Optional[_Union[WorldEventDetailEvent.UnknownFiveHundredFifteen.UnknownFiveHundredSixteen, str]] = ...) -> None: ...
    class UnknownFiveHundredSeventeen(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_EIGHT_HUNDRED_EIGHTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_eighty_two: WorldEventDetailEvent.UnknownFiveHundredFifteen
    def __init__(self, unknown_eight_hundred_eighty_two: _Optional[_Union[WorldEventDetailEvent.UnknownFiveHundredFifteen, _Mapping]] = ...) -> None: ...

class UnknownFiveHundredEleven(_message.Message):
    __slots__ = ("rank", "score", "unknown_eight_hundred_seventy_three", "player", "unknown_eight_hundred_seventy_four", "unknown_eight_hundred_seventy_five")
    RANK_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_THREE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    rank: int
    score: int
    unknown_eight_hundred_seventy_three: UnknownFiveHundredEight
    player: UnknownFiveHundredSeven
    unknown_eight_hundred_seventy_four: UnknownFiveHundredTen
    unknown_eight_hundred_seventy_five: UnknownFiveHundredFourteen
    def __init__(self, rank: _Optional[int] = ..., score: _Optional[int] = ..., unknown_eight_hundred_seventy_three: _Optional[_Union[UnknownFiveHundredEight, _Mapping]] = ..., player: _Optional[_Union[UnknownFiveHundredSeven, _Mapping]] = ..., unknown_eight_hundred_seventy_four: _Optional[_Union[UnknownFiveHundredTen, _Mapping]] = ..., unknown_eight_hundred_seventy_five: _Optional[_Union[UnknownFiveHundredFourteen, _Mapping]] = ...) -> None: ...

class UnknownFiveHundredEight(_message.Message):
    __slots__ = ("unknown_eight_hundred_sixty_eight",)
    UNKNOWN_EIGHT_HUNDRED_SIXTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_sixty_eight: int
    def __init__(self, unknown_eight_hundred_sixty_eight: _Optional[int] = ...) -> None: ...

class UnknownFiveHundredTen(_message.Message):
    __slots__ = ("unknown_eight_hundred_seventy_one", "unknown_eight_hundred_seventy_two")
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_seventy_one: _common_pb2.SocialEmblem
    unknown_eight_hundred_seventy_two: str
    def __init__(self, unknown_eight_hundred_seventy_one: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ..., unknown_eight_hundred_seventy_two: _Optional[str] = ...) -> None: ...

class UnknownFiveHundredFourteen(_message.Message):
    __slots__ = ("unknown_eight_hundred_seventy_eight", "unknown_eight_hundred_seventy_nine", "unknown_eight_hundred_eighty")
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_EIGHTY_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_seventy_eight: str
    unknown_eight_hundred_seventy_nine: int
    unknown_eight_hundred_eighty: _common_pb2.SocialEmblem
    def __init__(self, unknown_eight_hundred_seventy_eight: _Optional[str] = ..., unknown_eight_hundred_seventy_nine: _Optional[int] = ..., unknown_eight_hundred_eighty: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class WorldEventOccurrencesEvent(_message.Message):
    __slots__ = ("infos",)
    INFOS_FIELD_NUMBER: _ClassVar[int]
    infos: _containers.RepeatedCompositeFieldContainer[WorldEventOccurrence]
    def __init__(self, infos: _Optional[_Iterable[_Union[WorldEventOccurrence, _Mapping]]] = ...) -> None: ...

class UnknownFiveHundredNine(_message.Message):
    __slots__ = ("unknown_eight_hundred_sixty_nine", "unknown_eight_hundred_seventy")
    UNKNOWN_EIGHT_HUNDRED_SIXTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_sixty_nine: str
    unknown_eight_hundred_seventy: int
    def __init__(self, unknown_eight_hundred_sixty_nine: _Optional[str] = ..., unknown_eight_hundred_seventy: _Optional[int] = ...) -> None: ...

class UnknownFiveHundredTwelve(_message.Message):
    __slots__ = ("unknown_eight_hundred_seventy_six", "unknown_eight_hundred_seventy_seven")
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_SEVENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_seventy_six: str
    unknown_eight_hundred_seventy_seven: str
    def __init__(self, unknown_eight_hundred_seventy_six: _Optional[str] = ..., unknown_eight_hundred_seventy_seven: _Optional[str] = ...) -> None: ...

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

class UnknownFiveHundredThirteen(_message.Message):
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
