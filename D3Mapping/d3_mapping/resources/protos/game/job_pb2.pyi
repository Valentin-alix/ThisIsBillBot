import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobCrafterDirectoryListRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    def __init__(self, job_id: _Optional[int] = ...) -> None: ...

class JobCrafterDirectorySettingsRequest(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: JobCrafterDirectorySettings
    def __init__(self, settings: _Optional[_Union[JobCrafterDirectorySettings, _Mapping]] = ...) -> None: ...

class JobDescriptionEvent(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[JobDescription]
    def __init__(self, jobs: _Optional[_Iterable[_Union[JobDescription, _Mapping]]] = ...) -> None: ...

class JobLevelUpEvent(_message.Message):
    __slots__ = ("new_level", "job")
    NEW_LEVEL_FIELD_NUMBER: _ClassVar[int]
    JOB_FIELD_NUMBER: _ClassVar[int]
    new_level: int
    job: JobDescription
    def __init__(self, new_level: _Optional[int] = ..., job: _Optional[_Union[JobDescription, _Mapping]] = ...) -> None: ...

class JobExperiencesUpdateEvent(_message.Message):
    __slots__ = ("experiences",)
    EXPERIENCES_FIELD_NUMBER: _ClassVar[int]
    experiences: _containers.RepeatedCompositeFieldContainer[JobExperience]
    def __init__(self, experiences: _Optional[_Iterable[_Union[JobExperience, _Mapping]]] = ...) -> None: ...

class JobExperienceOtherPlayerUpdateEvent(_message.Message):
    __slots__ = ("experience", "player_id")
    EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    experience: JobExperience
    player_id: int
    def __init__(self, experience: _Optional[_Union[JobExperience, _Mapping]] = ..., player_id: _Optional[int] = ...) -> None: ...

class JobMultiCraftStateEvent(_message.Message):
    __slots__ = ("enabled", "player_skills")
    class PlayerSkills(_message.Message):
        __slots__ = ("player_id", "skills")
        PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
        SKILLS_FIELD_NUMBER: _ClassVar[int]
        player_id: int
        skills: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, player_id: _Optional[int] = ..., skills: _Optional[_Iterable[int]] = ...) -> None: ...
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PLAYER_SKILLS_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    player_skills: JobMultiCraftStateEvent.PlayerSkills
    def __init__(self, enabled: bool = ..., player_skills: _Optional[_Union[JobMultiCraftStateEvent.PlayerSkills, _Mapping]] = ...) -> None: ...

class JobCrafterDirectoryListEvent(_message.Message):
    __slots__ = ("list_entries",)
    LIST_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    list_entries: _containers.RepeatedCompositeFieldContainer[JobCrafterDirectoryEntry]
    def __init__(self, list_entries: _Optional[_Iterable[_Union[JobCrafterDirectoryEntry, _Mapping]]] = ...) -> None: ...

class JobCrafterDirectorySettingsEvent(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _containers.RepeatedCompositeFieldContainer[JobCrafterDirectorySettings]
    def __init__(self, settings: _Optional[_Iterable[_Union[JobCrafterDirectorySettings, _Mapping]]] = ...) -> None: ...

class JobBookSubscriptionEvent(_message.Message):
    __slots__ = ("subscriptions",)
    class Subscription(_message.Message):
        __slots__ = ("job_id", "subscribed")
        JOB_ID_FIELD_NUMBER: _ClassVar[int]
        SUBSCRIBED_FIELD_NUMBER: _ClassVar[int]
        job_id: int
        subscribed: bool
        def __init__(self, job_id: _Optional[int] = ..., subscribed: bool = ...) -> None: ...
    SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    subscriptions: _containers.RepeatedCompositeFieldContainer[JobBookSubscriptionEvent.Subscription]
    def __init__(self, subscriptions: _Optional[_Iterable[_Union[JobBookSubscriptionEvent.Subscription, _Mapping]]] = ...) -> None: ...

class JobCrafterDirectoryRemoveEvent(_message.Message):
    __slots__ = ("job_id", "player_id")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    player_id: int
    def __init__(self, job_id: _Optional[int] = ..., player_id: _Optional[int] = ...) -> None: ...

class JobCrafterDirectoryAddEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: JobCrafterDirectoryEntry
    def __init__(self, entry: _Optional[_Union[JobCrafterDirectoryEntry, _Mapping]] = ...) -> None: ...

class JobCrafterDirectoryEntryEvent(_message.Message):
    __slots__ = ("player_information", "jobs_information", "look")
    PLAYER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    JOBS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    LOOK_FIELD_NUMBER: _ClassVar[int]
    player_information: JobCrafterDirectoryPlayerInformation
    jobs_information: _containers.RepeatedCompositeFieldContainer[JobCrafterDirectoryJobInformation]
    look: _common_pb2.EntityLook
    def __init__(self, player_information: _Optional[_Union[JobCrafterDirectoryPlayerInformation, _Mapping]] = ..., jobs_information: _Optional[_Iterable[_Union[JobCrafterDirectoryJobInformation, _Mapping]]] = ..., look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class JobDescription(_message.Message):
    __slots__ = ("job_id", "skills")
    class SkillAction(_message.Message):
        __slots__ = ("skill_id", "timed", "craft")
        class Timed(_message.Message):
            __slots__ = ("time", "collect")
            class Collect(_message.Message):
                __slots__ = ("min", "max")
                MIN_FIELD_NUMBER: _ClassVar[int]
                MAX_FIELD_NUMBER: _ClassVar[int]
                min: int
                max: int
                def __init__(self, min: _Optional[int] = ..., max: _Optional[int] = ...) -> None: ...
            TIME_FIELD_NUMBER: _ClassVar[int]
            COLLECT_FIELD_NUMBER: _ClassVar[int]
            time: int
            collect: JobDescription.SkillAction.Timed.Collect
            def __init__(self, time: _Optional[int] = ..., collect: _Optional[_Union[JobDescription.SkillAction.Timed.Collect, _Mapping]] = ...) -> None: ...
        class Craft(_message.Message):
            __slots__ = ("probability",)
            PROBABILITY_FIELD_NUMBER: _ClassVar[int]
            probability: int
            def __init__(self, probability: _Optional[int] = ...) -> None: ...
        SKILL_ID_FIELD_NUMBER: _ClassVar[int]
        TIMED_FIELD_NUMBER: _ClassVar[int]
        CRAFT_FIELD_NUMBER: _ClassVar[int]
        skill_id: int
        timed: JobDescription.SkillAction.Timed
        craft: JobDescription.SkillAction.Craft
        def __init__(self, skill_id: _Optional[int] = ..., timed: _Optional[_Union[JobDescription.SkillAction.Timed, _Mapping]] = ..., craft: _Optional[_Union[JobDescription.SkillAction.Craft, _Mapping]] = ...) -> None: ...
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    SKILLS_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    skills: _containers.RepeatedCompositeFieldContainer[JobDescription.SkillAction]
    def __init__(self, job_id: _Optional[int] = ..., skills: _Optional[_Iterable[_Union[JobDescription.SkillAction, _Mapping]]] = ...) -> None: ...

class JobExperience(_message.Message):
    __slots__ = ("job_id", "job_level", "job_xp", "job_xp_level_floor", "job_xp_next_level_floor")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_LEVEL_FIELD_NUMBER: _ClassVar[int]
    JOB_XP_FIELD_NUMBER: _ClassVar[int]
    JOB_XP_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
    JOB_XP_NEXT_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    job_level: int
    job_xp: int
    job_xp_level_floor: int
    job_xp_next_level_floor: int
    def __init__(self, job_id: _Optional[int] = ..., job_level: _Optional[int] = ..., job_xp: _Optional[int] = ..., job_xp_level_floor: _Optional[int] = ..., job_xp_next_level_floor: _Optional[int] = ...) -> None: ...

class JobCrafterDirectoryEntry(_message.Message):
    __slots__ = ("player_information", "job_information")
    PLAYER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    JOB_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    player_information: JobCrafterDirectoryPlayerInformation
    job_information: JobCrafterDirectoryJobInformation
    def __init__(self, player_information: _Optional[_Union[JobCrafterDirectoryPlayerInformation, _Mapping]] = ..., job_information: _Optional[_Union[JobCrafterDirectoryJobInformation, _Mapping]] = ...) -> None: ...

class JobCrafterDirectoryPlayerInformation(_message.Message):
    __slots__ = ("player_id", "name", "alignment", "breed", "gender", "is_in_workshop", "coordinates", "can_craft_legendary", "status")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    BREED_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    IS_IN_WORKSHOP_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    CAN_CRAFT_LEGENDARY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    name: str
    alignment: _common_pb2.Alignment
    breed: int
    gender: _common_pb2.Gender
    is_in_workshop: bool
    coordinates: _common_pb2.MapExtendedCoordinates
    can_craft_legendary: bool
    status: _common_pb2.CharacterStatus
    def __init__(self, player_id: _Optional[int] = ..., name: _Optional[str] = ..., alignment: _Optional[_Union[_common_pb2.Alignment, str]] = ..., breed: _Optional[int] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ..., is_in_workshop: bool = ..., coordinates: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ..., can_craft_legendary: bool = ..., status: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ...) -> None: ...

class JobCrafterDirectoryJobInformation(_message.Message):
    __slots__ = ("job_id", "job_level", "free", "min_level")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_LEVEL_FIELD_NUMBER: _ClassVar[int]
    FREE_FIELD_NUMBER: _ClassVar[int]
    MIN_LEVEL_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    job_level: int
    free: bool
    min_level: int
    def __init__(self, job_id: _Optional[int] = ..., job_level: _Optional[int] = ..., free: bool = ..., min_level: _Optional[int] = ...) -> None: ...

class JobCrafterDirectorySettings(_message.Message):
    __slots__ = ("job_id", "min_level", "free")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    MIN_LEVEL_FIELD_NUMBER: _ClassVar[int]
    FREE_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    min_level: int
    free: bool
    def __init__(self, job_id: _Optional[int] = ..., min_level: _Optional[int] = ..., free: bool = ...) -> None: ...
