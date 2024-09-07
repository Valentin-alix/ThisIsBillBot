from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuestsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QuestStartRequest(_message.Message):
    __slots__ = ("quest_id",)
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    def __init__(self, quest_id: _Optional[int] = ...) -> None: ...

class QuestStepInformationRequest(_message.Message):
    __slots__ = ("quest_id",)
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    def __init__(self, quest_id: _Optional[int] = ...) -> None: ...

class QuestObjectiveValidationRequest(_message.Message):
    __slots__ = ("quest_id", "objective_id")
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    objective_id: int
    def __init__(self, quest_id: _Optional[int] = ..., objective_id: _Optional[int] = ...) -> None: ...

class GuideModReturnRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuideModQuitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QuestObjectiveFollowRequest(_message.Message):
    __slots__ = ("quest_id", "objective_id")
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    objective_id: int
    def __init__(self, quest_id: _Optional[int] = ..., objective_id: _Optional[int] = ...) -> None: ...

class QuestObjectiveUnfollowRequest(_message.Message):
    __slots__ = ("quest_id", "objective_id")
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    objective_id: int
    def __init__(self, quest_id: _Optional[int] = ..., objective_id: _Optional[int] = ...) -> None: ...

class QuestsFollowedOrderRefreshRequest(_message.Message):
    __slots__ = ("quests",)
    QUESTS_FIELD_NUMBER: _ClassVar[int]
    quests: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, quests: _Optional[_Iterable[int]] = ...) -> None: ...

class QuestsEvent(_message.Message):
    __slots__ = ("finished_quests", "active_quests", "reinitialized_done_quests_id", "player_id")
    class QuestFinished(_message.Message):
        __slots__ = ("quest_id", "finished_count")
        QUEST_ID_FIELD_NUMBER: _ClassVar[int]
        FINISHED_COUNT_FIELD_NUMBER: _ClassVar[int]
        quest_id: int
        finished_count: int
        def __init__(self, quest_id: _Optional[int] = ..., finished_count: _Optional[int] = ...) -> None: ...
    FINISHED_QUESTS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_QUESTS_FIELD_NUMBER: _ClassVar[int]
    REINITIALIZED_DONE_QUESTS_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    finished_quests: _containers.RepeatedCompositeFieldContainer[QuestsEvent.QuestFinished]
    active_quests: _containers.RepeatedCompositeFieldContainer[QuestActive]
    reinitialized_done_quests_id: _containers.RepeatedScalarFieldContainer[int]
    player_id: int
    def __init__(self, finished_quests: _Optional[_Iterable[_Union[QuestsEvent.QuestFinished, _Mapping]]] = ..., active_quests: _Optional[_Iterable[_Union[QuestActive, _Mapping]]] = ..., reinitialized_done_quests_id: _Optional[_Iterable[int]] = ..., player_id: _Optional[int] = ...) -> None: ...

class QuestStartedEvent(_message.Message):
    __slots__ = ("quest_id",)
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    def __init__(self, quest_id: _Optional[int] = ...) -> None: ...

class QuestValidatedEvent(_message.Message):
    __slots__ = ("quest_id",)
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    def __init__(self, quest_id: _Optional[int] = ...) -> None: ...

class QuestObjectiveValidatedEvent(_message.Message):
    __slots__ = ("quest_id", "objective_id")
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    objective_id: int
    def __init__(self, quest_id: _Optional[int] = ..., objective_id: _Optional[int] = ...) -> None: ...

class QuestStepValidatedEvent(_message.Message):
    __slots__ = ("quest_id", "step_id")
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    step_id: int
    def __init__(self, quest_id: _Optional[int] = ..., step_id: _Optional[int] = ...) -> None: ...

class QuestStepStartedEvent(_message.Message):
    __slots__ = ("quest_id", "step_id")
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    step_id: int
    def __init__(self, quest_id: _Optional[int] = ..., step_id: _Optional[int] = ...) -> None: ...

class QuestStepInformationEvent(_message.Message):
    __slots__ = ("information", "player_id")
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    information: QuestActive
    player_id: int
    def __init__(self, information: _Optional[_Union[QuestActive, _Mapping]] = ..., player_id: _Optional[int] = ...) -> None: ...

class QuestsFollowedEvent(_message.Message):
    __slots__ = ("quests",)
    QUESTS_FIELD_NUMBER: _ClassVar[int]
    quests: _containers.RepeatedCompositeFieldContainer[QuestActive]
    def __init__(self, quests: _Optional[_Iterable[_Union[QuestActive, _Mapping]]] = ...) -> None: ...

class QuestActive(_message.Message):
    __slots__ = ("quest_id", "details")
    class Details(_message.Message):
        __slots__ = ("step_id", "objectives")
        STEP_ID_FIELD_NUMBER: _ClassVar[int]
        OBJECTIVES_FIELD_NUMBER: _ClassVar[int]
        step_id: int
        objectives: _containers.RepeatedCompositeFieldContainer[QuestObjective]
        def __init__(self, step_id: _Optional[int] = ..., objectives: _Optional[_Iterable[_Union[QuestObjective, _Mapping]]] = ...) -> None: ...
    QUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    quest_id: int
    details: QuestActive.Details
    def __init__(self, quest_id: _Optional[int] = ..., details: _Optional[_Union[QuestActive.Details, _Mapping]] = ...) -> None: ...

class QuestObjective(_message.Message):
    __slots__ = ("objective_id", "objective_reached", "dialog_params", "completion")
    class Completion(_message.Message):
        __slots__ = ("current_completion", "max_completion")
        CURRENT_COMPLETION_FIELD_NUMBER: _ClassVar[int]
        MAX_COMPLETION_FIELD_NUMBER: _ClassVar[int]
        current_completion: int
        max_completion: int
        def __init__(self, current_completion: _Optional[int] = ..., max_completion: _Optional[int] = ...) -> None: ...
    OBJECTIVE_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_REACHED_FIELD_NUMBER: _ClassVar[int]
    DIALOG_PARAMS_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_FIELD_NUMBER: _ClassVar[int]
    objective_id: int
    objective_reached: bool
    dialog_params: _containers.RepeatedScalarFieldContainer[str]
    completion: QuestObjective.Completion
    def __init__(self, objective_id: _Optional[int] = ..., objective_reached: bool = ..., dialog_params: _Optional[_Iterable[str]] = ..., completion: _Optional[_Union[QuestObjective.Completion, _Mapping]] = ...) -> None: ...
