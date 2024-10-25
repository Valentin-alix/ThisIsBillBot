import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TreasureHuntType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLASSIC: _ClassVar[TreasureHuntType]
    PORTAL: _ClassVar[TreasureHuntType]
    LEGENDARY: _ClassVar[TreasureHuntType]
CLASSIC: TreasureHuntType
PORTAL: TreasureHuntType
LEGENDARY: TreasureHuntType

class TreasureHuntLegendaryRequest(_message.Message):
    __slots__ = ("legendary_id",)
    LEGENDARY_ID_FIELD_NUMBER: _ClassVar[int]
    legendary_id: int
    def __init__(self, legendary_id: _Optional[int] = ...) -> None: ...

class TreasureHuntDigRequest(_message.Message):
    __slots__ = ("quest_type",)
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ...) -> None: ...

class TreasureHuntFlagRequest(_message.Message):
    __slots__ = ("quest_type", "index")
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    index: int
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ..., index: _Optional[int] = ...) -> None: ...

class TreasureHuntFlagRemoveRequest(_message.Message):
    __slots__ = ("quest_type", "index")
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    index: int
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ..., index: _Optional[int] = ...) -> None: ...

class TreasureHuntGiveUpRequest(_message.Message):
    __slots__ = ("quest_type",)
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ...) -> None: ...

class PortalUseRequest(_message.Message):
    __slots__ = ("portal_id",)
    PORTAL_ID_FIELD_NUMBER: _ClassVar[int]
    portal_id: int
    def __init__(self, portal_id: _Optional[int] = ...) -> None: ...

class TreasureHuntLegendaryEvent(_message.Message):
    __slots__ = ("available_legendary_ids",)
    AVAILABLE_LEGENDARY_IDS_FIELD_NUMBER: _ClassVar[int]
    available_legendary_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, available_legendary_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class TreasureHuntAnswerEvent(_message.Message):
    __slots__ = ("quest_type", "result")
    class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ERROR_UNDEFINED: _ClassVar[TreasureHuntAnswerEvent.Result]
        ERROR_NO_QUEST_FOUND: _ClassVar[TreasureHuntAnswerEvent.Result]
        ERROR_ALREADY_HAVE_QUEST: _ClassVar[TreasureHuntAnswerEvent.Result]
        ERROR_NOT_AVAILABLE: _ClassVar[TreasureHuntAnswerEvent.Result]
        ERROR_DAILY_LIMIT_EXCEEDED: _ClassVar[TreasureHuntAnswerEvent.Result]
        OK: _ClassVar[TreasureHuntAnswerEvent.Result]
    ERROR_UNDEFINED: TreasureHuntAnswerEvent.Result
    ERROR_NO_QUEST_FOUND: TreasureHuntAnswerEvent.Result
    ERROR_ALREADY_HAVE_QUEST: TreasureHuntAnswerEvent.Result
    ERROR_NOT_AVAILABLE: TreasureHuntAnswerEvent.Result
    ERROR_DAILY_LIMIT_EXCEEDED: TreasureHuntAnswerEvent.Result
    OK: TreasureHuntAnswerEvent.Result
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    result: TreasureHuntAnswerEvent.Result
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ..., result: _Optional[_Union[TreasureHuntAnswerEvent.Result, str]] = ...) -> None: ...

class TreasureHuntEvent(_message.Message):
    __slots__ = ("quest_type", "start_map_id", "known_steps", "total_step_count", "current_check_point", "total_check_point", "available_retry_count", "flags")
    class TreasureHuntStep(_message.Message):
        __slots__ = ("follow_direction_to_poi", "follow_direction_to_hint", "follow_direction", "fight", "dig")
        class FollowDirectionToPOI(_message.Message):
            __slots__ = ("direction", "poi_label_id")
            DIRECTION_FIELD_NUMBER: _ClassVar[int]
            POI_LABEL_ID_FIELD_NUMBER: _ClassVar[int]
            direction: _common_pb2.Direction
            poi_label_id: int
            def __init__(self, direction: _Optional[_Union[_common_pb2.Direction, str]] = ..., poi_label_id: _Optional[int] = ...) -> None: ...
        class FollowDirectionToHint(_message.Message):
            __slots__ = ("direction", "npc_id")
            DIRECTION_FIELD_NUMBER: _ClassVar[int]
            NPC_ID_FIELD_NUMBER: _ClassVar[int]
            direction: _common_pb2.Direction
            npc_id: int
            def __init__(self, direction: _Optional[_Union[_common_pb2.Direction, str]] = ..., npc_id: _Optional[int] = ...) -> None: ...
        class FollowDirection(_message.Message):
            __slots__ = ("direction", "map_count")
            DIRECTION_FIELD_NUMBER: _ClassVar[int]
            MAP_COUNT_FIELD_NUMBER: _ClassVar[int]
            direction: _common_pb2.Direction
            map_count: int
            def __init__(self, direction: _Optional[_Union[_common_pb2.Direction, str]] = ..., map_count: _Optional[int] = ...) -> None: ...
        class Fight(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class Dig(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        FOLLOW_DIRECTION_TO_POI_FIELD_NUMBER: _ClassVar[int]
        FOLLOW_DIRECTION_TO_HINT_FIELD_NUMBER: _ClassVar[int]
        FOLLOW_DIRECTION_FIELD_NUMBER: _ClassVar[int]
        FIGHT_FIELD_NUMBER: _ClassVar[int]
        DIG_FIELD_NUMBER: _ClassVar[int]
        follow_direction_to_poi: TreasureHuntEvent.TreasureHuntStep.FollowDirectionToPOI
        follow_direction_to_hint: TreasureHuntEvent.TreasureHuntStep.FollowDirectionToHint
        follow_direction: TreasureHuntEvent.TreasureHuntStep.FollowDirection
        fight: TreasureHuntEvent.TreasureHuntStep.Fight
        dig: TreasureHuntEvent.TreasureHuntStep.Dig
        def __init__(self, follow_direction_to_poi: _Optional[_Union[TreasureHuntEvent.TreasureHuntStep.FollowDirectionToPOI, _Mapping]] = ..., follow_direction_to_hint: _Optional[_Union[TreasureHuntEvent.TreasureHuntStep.FollowDirectionToHint, _Mapping]] = ..., follow_direction: _Optional[_Union[TreasureHuntEvent.TreasureHuntStep.FollowDirection, _Mapping]] = ..., fight: _Optional[_Union[TreasureHuntEvent.TreasureHuntStep.Fight, _Mapping]] = ..., dig: _Optional[_Union[TreasureHuntEvent.TreasureHuntStep.Dig, _Mapping]] = ...) -> None: ...
    class TreasureHuntFlag(_message.Message):
        __slots__ = ("map_id", "state")
        class FlagState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN: _ClassVar[TreasureHuntEvent.TreasureHuntFlag.FlagState]
            OK: _ClassVar[TreasureHuntEvent.TreasureHuntFlag.FlagState]
            WRONG: _ClassVar[TreasureHuntEvent.TreasureHuntFlag.FlagState]
        UNKNOWN: TreasureHuntEvent.TreasureHuntFlag.FlagState
        OK: TreasureHuntEvent.TreasureHuntFlag.FlagState
        WRONG: TreasureHuntEvent.TreasureHuntFlag.FlagState
        MAP_ID_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        map_id: int
        state: TreasureHuntEvent.TreasureHuntFlag.FlagState
        def __init__(self, map_id: _Optional[int] = ..., state: _Optional[_Union[TreasureHuntEvent.TreasureHuntFlag.FlagState, str]] = ...) -> None: ...
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    START_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    KNOWN_STEPS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_STEP_COUNT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_CHECK_POINT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHECK_POINT_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_RETRY_COUNT_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    start_map_id: int
    known_steps: _containers.RepeatedCompositeFieldContainer[TreasureHuntEvent.TreasureHuntStep]
    total_step_count: int
    current_check_point: int
    total_check_point: int
    available_retry_count: int
    flags: _containers.RepeatedCompositeFieldContainer[TreasureHuntEvent.TreasureHuntFlag]
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ..., start_map_id: _Optional[int] = ..., known_steps: _Optional[_Iterable[_Union[TreasureHuntEvent.TreasureHuntStep, _Mapping]]] = ..., total_step_count: _Optional[int] = ..., current_check_point: _Optional[int] = ..., total_check_point: _Optional[int] = ..., available_retry_count: _Optional[int] = ..., flags: _Optional[_Iterable[_Union[TreasureHuntEvent.TreasureHuntFlag, _Mapping]]] = ...) -> None: ...

class TreasureHuntFinishedEvent(_message.Message):
    __slots__ = ("quest_type",)
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ...) -> None: ...

class TreasureHuntDigAnswerEvent(_message.Message):
    __slots__ = ("quest_type", "result", "wrong_flag_count")
    class DigResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ERROR_UNDEFINED: _ClassVar[TreasureHuntDigAnswerEvent.DigResult]
        NEW_HINT: _ClassVar[TreasureHuntDigAnswerEvent.DigResult]
        FINISHED: _ClassVar[TreasureHuntDigAnswerEvent.DigResult]
        WRONG: _ClassVar[TreasureHuntDigAnswerEvent.DigResult]
        LOST: _ClassVar[TreasureHuntDigAnswerEvent.DigResult]
        ERROR_IMPOSSIBLE: _ClassVar[TreasureHuntDigAnswerEvent.DigResult]
        WRONG_AND_YOU_KNOW_IT: _ClassVar[TreasureHuntDigAnswerEvent.DigResult]
    ERROR_UNDEFINED: TreasureHuntDigAnswerEvent.DigResult
    NEW_HINT: TreasureHuntDigAnswerEvent.DigResult
    FINISHED: TreasureHuntDigAnswerEvent.DigResult
    WRONG: TreasureHuntDigAnswerEvent.DigResult
    LOST: TreasureHuntDigAnswerEvent.DigResult
    ERROR_IMPOSSIBLE: TreasureHuntDigAnswerEvent.DigResult
    WRONG_AND_YOU_KNOW_IT: TreasureHuntDigAnswerEvent.DigResult
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    WRONG_FLAG_COUNT_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    result: TreasureHuntDigAnswerEvent.DigResult
    wrong_flag_count: int
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ..., result: _Optional[_Union[TreasureHuntDigAnswerEvent.DigResult, str]] = ..., wrong_flag_count: _Optional[int] = ...) -> None: ...

class TreasureHuntFlagAnswerEvent(_message.Message):
    __slots__ = ("quest_type", "result", "index")
    class FlagResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ERROR_UNDEFINED: _ClassVar[TreasureHuntFlagAnswerEvent.FlagResult]
        OK: _ClassVar[TreasureHuntFlagAnswerEvent.FlagResult]
        WRONG: _ClassVar[TreasureHuntFlagAnswerEvent.FlagResult]
        TOO_MANY: _ClassVar[TreasureHuntFlagAnswerEvent.FlagResult]
        ERROR_IMPOSSIBLE: _ClassVar[TreasureHuntFlagAnswerEvent.FlagResult]
        WRONG_INDEX: _ClassVar[TreasureHuntFlagAnswerEvent.FlagResult]
        SAME_MAP: _ClassVar[TreasureHuntFlagAnswerEvent.FlagResult]
    ERROR_UNDEFINED: TreasureHuntFlagAnswerEvent.FlagResult
    OK: TreasureHuntFlagAnswerEvent.FlagResult
    WRONG: TreasureHuntFlagAnswerEvent.FlagResult
    TOO_MANY: TreasureHuntFlagAnswerEvent.FlagResult
    ERROR_IMPOSSIBLE: TreasureHuntFlagAnswerEvent.FlagResult
    WRONG_INDEX: TreasureHuntFlagAnswerEvent.FlagResult
    SAME_MAP: TreasureHuntFlagAnswerEvent.FlagResult
    QUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    quest_type: TreasureHuntType
    result: TreasureHuntFlagAnswerEvent.FlagResult
    index: int
    def __init__(self, quest_type: _Optional[_Union[TreasureHuntType, str]] = ..., result: _Optional[_Union[TreasureHuntFlagAnswerEvent.FlagResult, str]] = ..., index: _Optional[int] = ...) -> None: ...
