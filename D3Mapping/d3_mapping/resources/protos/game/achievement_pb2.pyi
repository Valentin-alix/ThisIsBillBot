from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AchievementDetailsRequest(_message.Message):
    __slots__ = ("achievement_id",)
    ACHIEVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    achievement_id: int
    def __init__(self, achievement_id: _Optional[int] = ...) -> None: ...

class AchievementsDetailedRequest(_message.Message):
    __slots__ = ("category_id",)
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    def __init__(self, category_id: _Optional[int] = ...) -> None: ...

class AchievementsAlmostFinishedDetailedRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AchievementRewardRequest(_message.Message):
    __slots__ = ("achievement_id",)
    ACHIEVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    achievement_id: int
    def __init__(self, achievement_id: _Optional[int] = ...) -> None: ...

class AchievementsEvent(_message.Message):
    __slots__ = ("achieved_achievements",)
    ACHIEVED_ACHIEVEMENTS_FIELD_NUMBER: _ClassVar[int]
    achieved_achievements: _containers.RepeatedCompositeFieldContainer[AchievedAchievement]
    def __init__(self, achieved_achievements: _Optional[_Iterable[_Union[AchievedAchievement, _Mapping]]] = ...) -> None: ...

class AchievementDetailsEvent(_message.Message):
    __slots__ = ("achievement",)
    ACHIEVEMENT_FIELD_NUMBER: _ClassVar[int]
    achievement: Achievement
    def __init__(self, achievement: _Optional[_Union[Achievement, _Mapping]] = ...) -> None: ...

class AchievementsDetailedEvent(_message.Message):
    __slots__ = ("achievements",)
    ACHIEVEMENTS_FIELD_NUMBER: _ClassVar[int]
    achievements: _containers.RepeatedCompositeFieldContainer[Achievement]
    def __init__(self, achievements: _Optional[_Iterable[_Union[Achievement, _Mapping]]] = ...) -> None: ...

class AchievementsAlmostFinishedDetailedEvent(_message.Message):
    __slots__ = ("almost_finished_achievements",)
    ALMOST_FINISHED_ACHIEVEMENTS_FIELD_NUMBER: _ClassVar[int]
    almost_finished_achievements: _containers.RepeatedCompositeFieldContainer[Achievement]
    def __init__(self, almost_finished_achievements: _Optional[_Iterable[_Union[Achievement, _Mapping]]] = ...) -> None: ...

class AchievementFinishedEvent(_message.Message):
    __slots__ = ("achievement",)
    ACHIEVEMENT_FIELD_NUMBER: _ClassVar[int]
    achievement: AchievedAchievement
    def __init__(self, achievement: _Optional[_Union[AchievedAchievement, _Mapping]] = ...) -> None: ...

class AchievementFinishedInformationEvent(_message.Message):
    __slots__ = ("achievement", "player_name", "player_id")
    ACHIEVEMENT_FIELD_NUMBER: _ClassVar[int]
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    achievement: AchievedAchievement
    player_name: str
    player_id: int
    def __init__(self, achievement: _Optional[_Union[AchievedAchievement, _Mapping]] = ..., player_name: _Optional[str] = ..., player_id: _Optional[int] = ...) -> None: ...

class AchievementRewardResultEvent(_message.Message):
    __slots__ = ("achievement_id", "success")
    ACHIEVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    achievement_id: int
    success: bool
    def __init__(self, achievement_id: _Optional[int] = ..., success: bool = ...) -> None: ...

class AchievementsPioneerRanksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AchievementsPioneerRanksResponse(_message.Message):
    __slots__ = ("achievements_pioneer_ranks",)
    class AchievementPioneerRank(_message.Message):
        __slots__ = ("achievement_id", "pioneer_rank")
        ACHIEVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
        PIONEER_RANK_FIELD_NUMBER: _ClassVar[int]
        achievement_id: int
        pioneer_rank: int
        def __init__(self, achievement_id: _Optional[int] = ..., pioneer_rank: _Optional[int] = ...) -> None: ...
    ACHIEVEMENTS_PIONEER_RANKS_FIELD_NUMBER: _ClassVar[int]
    achievements_pioneer_ranks: _containers.RepeatedCompositeFieldContainer[AchievementsPioneerRanksResponse.AchievementPioneerRank]
    def __init__(self, achievements_pioneer_ranks: _Optional[_Iterable[_Union[AchievementsPioneerRanksResponse.AchievementPioneerRank, _Mapping]]] = ...) -> None: ...

class Achievement(_message.Message):
    __slots__ = ("achievement_id", "achievement_objectives")
    class AchievementObjective(_message.Message):
        __slots__ = ("objective_id", "max_value", "current_value")
        OBJECTIVE_ID_FIELD_NUMBER: _ClassVar[int]
        MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
        CURRENT_VALUE_FIELD_NUMBER: _ClassVar[int]
        objective_id: int
        max_value: int
        current_value: int
        def __init__(self, objective_id: _Optional[int] = ..., max_value: _Optional[int] = ..., current_value: _Optional[int] = ...) -> None: ...
    ACHIEVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ACHIEVEMENT_OBJECTIVES_FIELD_NUMBER: _ClassVar[int]
    achievement_id: int
    achievement_objectives: _containers.RepeatedCompositeFieldContainer[Achievement.AchievementObjective]
    def __init__(self, achievement_id: _Optional[int] = ..., achievement_objectives: _Optional[_Iterable[_Union[Achievement.AchievementObjective, _Mapping]]] = ...) -> None: ...

class AchievedAchievement(_message.Message):
    __slots__ = ("achievement_id", "achieved_by", "pioneer_rank", "finished_level")
    ACHIEVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ACHIEVED_BY_FIELD_NUMBER: _ClassVar[int]
    PIONEER_RANK_FIELD_NUMBER: _ClassVar[int]
    FINISHED_LEVEL_FIELD_NUMBER: _ClassVar[int]
    achievement_id: int
    achieved_by: int
    pioneer_rank: int
    finished_level: int
    def __init__(self, achievement_id: _Optional[int] = ..., achieved_by: _Optional[int] = ..., pioneer_rank: _Optional[int] = ..., finished_level: _Optional[int] = ...) -> None: ...
