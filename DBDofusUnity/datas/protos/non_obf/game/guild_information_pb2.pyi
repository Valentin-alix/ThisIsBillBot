import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildLogbookRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildSummaryRequest(_message.Message):
    __slots__ = ("offset", "count", "name_filter", "hide_full_filter", "following_guild_criteria", "criterion_filter", "languages_filter", "recruitment_type_filters", "min_level_filter", "max_level_filter", "min_player_level_filter", "max_player_level_filter", "min_success_filter", "max_success_filter", "sort_type", "sort_descending")
    class SummarySort(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SORT_BY_NAME: _ClassVar[GuildSummaryRequest.SummarySort]
        SORT_BY_LEVEL: _ClassVar[GuildSummaryRequest.SummarySort]
        SORT_BY_NB_MEMBERS: _ClassVar[GuildSummaryRequest.SummarySort]
        SORT_BY_LAST_ACTIVITY: _ClassVar[GuildSummaryRequest.SummarySort]
    SORT_BY_NAME: GuildSummaryRequest.SummarySort
    SORT_BY_LEVEL: GuildSummaryRequest.SummarySort
    SORT_BY_NB_MEMBERS: GuildSummaryRequest.SummarySort
    SORT_BY_LAST_ACTIVITY: GuildSummaryRequest.SummarySort
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    NAME_FILTER_FIELD_NUMBER: _ClassVar[int]
    HIDE_FULL_FILTER_FIELD_NUMBER: _ClassVar[int]
    FOLLOWING_GUILD_CRITERIA_FIELD_NUMBER: _ClassVar[int]
    CRITERION_FILTER_FIELD_NUMBER: _ClassVar[int]
    LANGUAGES_FILTER_FIELD_NUMBER: _ClassVar[int]
    RECRUITMENT_TYPE_FILTERS_FIELD_NUMBER: _ClassVar[int]
    MIN_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    MIN_PLAYER_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_PLAYER_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    MIN_SUCCESS_FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_SUCCESS_FILTER_FIELD_NUMBER: _ClassVar[int]
    SORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SORT_DESCENDING_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    name_filter: str
    hide_full_filter: bool
    following_guild_criteria: bool
    criterion_filter: _containers.RepeatedScalarFieldContainer[int]
    languages_filter: _containers.RepeatedScalarFieldContainer[int]
    recruitment_type_filters: _containers.RepeatedScalarFieldContainer[_common_pb2.SocialRecruitmentType]
    min_level_filter: int
    max_level_filter: int
    min_player_level_filter: int
    max_player_level_filter: int
    min_success_filter: int
    max_success_filter: int
    sort_type: GuildSummaryRequest.SummarySort
    sort_descending: bool
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ..., name_filter: _Optional[str] = ..., hide_full_filter: bool = ..., following_guild_criteria: bool = ..., criterion_filter: _Optional[_Iterable[int]] = ..., languages_filter: _Optional[_Iterable[int]] = ..., recruitment_type_filters: _Optional[_Iterable[_Union[_common_pb2.SocialRecruitmentType, str]]] = ..., min_level_filter: _Optional[int] = ..., max_level_filter: _Optional[int] = ..., min_player_level_filter: _Optional[int] = ..., max_player_level_filter: _Optional[int] = ..., min_success_filter: _Optional[int] = ..., max_success_filter: _Optional[int] = ..., sort_type: _Optional[_Union[GuildSummaryRequest.SummarySort, str]] = ..., sort_descending: bool = ...) -> None: ...

class GuildInformationRequest(_message.Message):
    __slots__ = ("information_type",)
    class InformationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INFO_GENERAL: _ClassVar[GuildInformationRequest.InformationType]
        INFO_MEMBERS: _ClassVar[GuildInformationRequest.InformationType]
        INFO_BOOSTS: _ClassVar[GuildInformationRequest.InformationType]
        INFO_PADDOCKS: _ClassVar[GuildInformationRequest.InformationType]
        INFO_HOUSES: _ClassVar[GuildInformationRequest.InformationType]
        INFO_RECRUITMENT: _ClassVar[GuildInformationRequest.InformationType]
        INFO_LOGBOOK: _ClassVar[GuildInformationRequest.InformationType]
    INFO_GENERAL: GuildInformationRequest.InformationType
    INFO_MEMBERS: GuildInformationRequest.InformationType
    INFO_BOOSTS: GuildInformationRequest.InformationType
    INFO_PADDOCKS: GuildInformationRequest.InformationType
    INFO_HOUSES: GuildInformationRequest.InformationType
    INFO_RECRUITMENT: GuildInformationRequest.InformationType
    INFO_LOGBOOK: GuildInformationRequest.InformationType
    INFORMATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    information_type: GuildInformationRequest.InformationType
    def __init__(self, information_type: _Optional[_Union[GuildInformationRequest.InformationType, str]] = ...) -> None: ...

class GuildModificationNameValidRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GuildModificationEmblemValidRequest(_message.Message):
    __slots__ = ("emblem",)
    EMBLEM_FIELD_NUMBER: _ClassVar[int]
    emblem: _common_pb2.SocialEmblem
    def __init__(self, emblem: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class GuildModificationValidRequest(_message.Message):
    __slots__ = ("name", "emblem")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMBLEM_FIELD_NUMBER: _ClassVar[int]
    name: str
    emblem: _common_pb2.SocialEmblem
    def __init__(self, name: _Optional[str] = ..., emblem: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class GuildCreationValidRequest(_message.Message):
    __slots__ = ("name", "emblem")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMBLEM_FIELD_NUMBER: _ClassVar[int]
    name: str
    emblem: _common_pb2.SocialEmblem
    def __init__(self, name: _Optional[str] = ..., emblem: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class GuildInvitationRequest(_message.Message):
    __slots__ = ("target_id",)
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    target_id: int
    def __init__(self, target_id: _Optional[int] = ...) -> None: ...

class GuildInvitationAnswerRequest(_message.Message):
    __slots__ = ("accepted",)
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    def __init__(self, accepted: bool = ...) -> None: ...

class GuildKickRequest(_message.Message):
    __slots__ = ("kicked_id",)
    KICKED_ID_FIELD_NUMBER: _ClassVar[int]
    kicked_id: int
    def __init__(self, kicked_id: _Optional[int] = ...) -> None: ...

class GuildMotdSetRequest(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class GuildBulletinSetRequest(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class GuildCardRequest(_message.Message):
    __slots__ = ("guild_id",)
    GUILD_ID_FIELD_NUMBER: _ClassVar[int]
    guild_id: int
    def __init__(self, guild_id: _Optional[int] = ...) -> None: ...

class GuildNoteUpdateRequest(_message.Message):
    __slots__ = ("player_id", "note")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    note: str
    def __init__(self, player_id: _Optional[int] = ..., note: _Optional[str] = ...) -> None: ...

class GuildLogbookEvent(_message.Message):
    __slots__ = ("global_activities", "chest_activities", "unknown_four_hundred_sixty_seven", "unknown_four_hundred_sixty_eight")
    GLOBAL_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    CHEST_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SIXTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SIXTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    global_activities: _containers.RepeatedCompositeFieldContainer[_common_pb2.GuildLogbookEntry]
    chest_activities: _containers.RepeatedCompositeFieldContainer[_common_pb2.GuildLogbookEntry]
    unknown_four_hundred_sixty_seven: _containers.RepeatedCompositeFieldContainer[_common_pb2.GuildLogbookEntry]
    unknown_four_hundred_sixty_eight: _containers.RepeatedCompositeFieldContainer[_common_pb2.GuildLogbookEntry]
    def __init__(self, global_activities: _Optional[_Iterable[_Union[_common_pb2.GuildLogbookEntry, _Mapping]]] = ..., chest_activities: _Optional[_Iterable[_Union[_common_pb2.GuildLogbookEntry, _Mapping]]] = ..., unknown_four_hundred_sixty_seven: _Optional[_Iterable[_Union[_common_pb2.GuildLogbookEntry, _Mapping]]] = ..., unknown_four_hundred_sixty_eight: _Optional[_Iterable[_Union[_common_pb2.GuildLogbookEntry, _Mapping]]] = ...) -> None: ...

class GuildSummaryEvent(_message.Message):
    __slots__ = ("offset", "count", "total", "guilds")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    GUILDS_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    total: int
    guilds: _containers.RepeatedCompositeFieldContainer[_common_pb2.GuildInformation]
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ..., total: _Optional[int] = ..., guilds: _Optional[_Iterable[_Union[_common_pb2.GuildInformation, _Mapping]]] = ...) -> None: ...

class GuildModificationStartedEvent(_message.Message):
    __slots__ = ("can_change_name", "can_change_emblem")
    CAN_CHANGE_NAME_FIELD_NUMBER: _ClassVar[int]
    CAN_CHANGE_EMBLEM_FIELD_NUMBER: _ClassVar[int]
    can_change_name: bool
    can_change_emblem: bool
    def __init__(self, can_change_name: bool = ..., can_change_emblem: bool = ...) -> None: ...

class GuildCreationResultEvent(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.SocialGroupOperationResult
    def __init__(self, result: _Optional[_Union[_common_pb2.SocialGroupOperationResult, str]] = ...) -> None: ...

class GuildModificationResultEvent(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.SocialGroupOperationResult
    def __init__(self, result: _Optional[_Union[_common_pb2.SocialGroupOperationResult, str]] = ...) -> None: ...

class GuildInvitedEvent(_message.Message):
    __slots__ = ("recruiter_name", "guild_information")
    RECRUITER_NAME_FIELD_NUMBER: _ClassVar[int]
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    recruiter_name: str
    guild_information: _common_pb2.GuildInformation
    def __init__(self, recruiter_name: _Optional[str] = ..., guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ...) -> None: ...

class GuildInvitationStateRecruiterEvent(_message.Message):
    __slots__ = ("recruited_name", "invitation_state", "recruited_id")
    RECRUITED_NAME_FIELD_NUMBER: _ClassVar[int]
    INVITATION_STATE_FIELD_NUMBER: _ClassVar[int]
    RECRUITED_ID_FIELD_NUMBER: _ClassVar[int]
    recruited_name: str
    invitation_state: _common_pb2.SocialGroupInvitationState
    recruited_id: int
    def __init__(self, recruited_name: _Optional[str] = ..., invitation_state: _Optional[_Union[_common_pb2.SocialGroupInvitationState, str]] = ..., recruited_id: _Optional[int] = ...) -> None: ...

class GuildInvitationStateRecruitedEvent(_message.Message):
    __slots__ = ("invitation_state",)
    INVITATION_STATE_FIELD_NUMBER: _ClassVar[int]
    invitation_state: _common_pb2.SocialGroupInvitationState
    def __init__(self, invitation_state: _Optional[_Union[_common_pb2.SocialGroupInvitationState, str]] = ...) -> None: ...

class GuildGeneralInformationEvent(_message.Message):
    __slots__ = ("abandoned_paddock", "level", "exp_level_floor", "experience", "exp_level_next_floor", "creation_date", "members_count", "score")
    ABANDONED_PADDOCK_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    EXP_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    EXP_LEVEL_NEXT_FLOOR_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    abandoned_paddock: bool
    level: int
    exp_level_floor: int
    experience: int
    exp_level_next_floor: int
    creation_date: str
    members_count: int
    score: int
    def __init__(self, abandoned_paddock: bool = ..., level: _Optional[int] = ..., exp_level_floor: _Optional[int] = ..., experience: _Optional[int] = ..., exp_level_next_floor: _Optional[int] = ..., creation_date: _Optional[str] = ..., members_count: _Optional[int] = ..., score: _Optional[int] = ...) -> None: ...

class GuildPaddockRemovedEvent(_message.Message):
    __slots__ = ("paddock_id",)
    PADDOCK_ID_FIELD_NUMBER: _ClassVar[int]
    paddock_id: int
    def __init__(self, paddock_id: _Optional[int] = ...) -> None: ...

class GuildMotdEvent(_message.Message):
    __slots__ = ("motd",)
    MOTD_FIELD_NUMBER: _ClassVar[int]
    motd: _common_pb2.SocialNoticeInformation
    def __init__(self, motd: _Optional[_Union[_common_pb2.SocialNoticeInformation, _Mapping]] = ...) -> None: ...

class GuildMotdSetErrorEvent(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.SocialNoticeError
    def __init__(self, error: _Optional[_Union[_common_pb2.SocialNoticeError, str]] = ...) -> None: ...

class GuildBulletinEvent(_message.Message):
    __slots__ = ("bulletin",)
    BULLETIN_FIELD_NUMBER: _ClassVar[int]
    bulletin: _common_pb2.SocialNoticeInformation
    def __init__(self, bulletin: _Optional[_Union[_common_pb2.SocialNoticeInformation, _Mapping]] = ...) -> None: ...

class GuildBulletinSetErrorEvent(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.SocialNoticeError
    def __init__(self, error: _Optional[_Union[_common_pb2.SocialNoticeError, str]] = ...) -> None: ...

class GuildCardErrorEvent(_message.Message):
    __slots__ = ("guild_id",)
    GUILD_ID_FIELD_NUMBER: _ClassVar[int]
    guild_id: int
    def __init__(self, guild_id: _Optional[int] = ...) -> None: ...

class GuildCardEvent(_message.Message):
    __slots__ = ("info", "creation_date", "members")
    INFO_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    info: _common_pb2.GuildInformation
    creation_date: int
    members: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    def __init__(self, info: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., creation_date: _Optional[int] = ..., members: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ...) -> None: ...

class GuildFeaturePanelStateRequest(_message.Message):
    __slots__ = ("is_open", "unknown_four_hundred_sixty_two")
    class UnknownTwoHundredThirtyEight(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TWO_HUNDRED_THIRTY_EIGHT_UNSPECIFIED: _ClassVar[GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight]
        UNKNOWN_TWO_HUNDRED_THIRTY_EIGHT_1: _ClassVar[GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight]
        UNKNOWN_TWO_HUNDRED_THIRTY_EIGHT_2: _ClassVar[GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight]
    UNKNOWN_TWO_HUNDRED_THIRTY_EIGHT_UNSPECIFIED: GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight
    UNKNOWN_TWO_HUNDRED_THIRTY_EIGHT_1: GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight
    UNKNOWN_TWO_HUNDRED_THIRTY_EIGHT_2: GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight
    IS_OPEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SIXTY_TWO_FIELD_NUMBER: _ClassVar[int]
    is_open: bool
    unknown_four_hundred_sixty_two: GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight
    def __init__(self, is_open: bool = ..., unknown_four_hundred_sixty_two: _Optional[_Union[GuildFeaturePanelStateRequest.UnknownTwoHundredThirtyEight, str]] = ...) -> None: ...

class UnknownTwoHundredThirtyNine(_message.Message):
    __slots__ = ("unknown_four_hundred_sixty_nine", "unknown_four_hundred_seventy")
    class UnknownFourHundredSeventyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: bool
        value: int
        def __init__(self, key: bool = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FOUR_HUNDRED_SIXTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SEVENTY_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_sixty_nine: str
    unknown_four_hundred_seventy: _containers.ScalarMap[bool, int]
    def __init__(self, unknown_four_hundred_sixty_nine: _Optional[str] = ..., unknown_four_hundred_seventy: _Optional[_Mapping[bool, int]] = ...) -> None: ...

class GuildHallConfigurationEvent(_message.Message):
    __slots__ = ("configuration",)
    class GuildHallConfiguration(_message.Message):
        __slots__ = ("unknown_four_hundred_sixty_three", "available_options_by_key", "available_option_ids", "is_enabled", "unknown_four_hundred_sixty_four", "unknown_four_hundred_sixty_five", "unknown_four_hundred_sixty_six")
        class AvailableOptionsByKeyEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: bool
            def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
        UNKNOWN_FOUR_HUNDRED_SIXTY_THREE_FIELD_NUMBER: _ClassVar[int]
        AVAILABLE_OPTIONS_BY_KEY_FIELD_NUMBER: _ClassVar[int]
        AVAILABLE_OPTION_IDS_FIELD_NUMBER: _ClassVar[int]
        IS_ENABLED_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_SIXTY_FOUR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_SIXTY_FIVE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_SIXTY_SIX_FIELD_NUMBER: _ClassVar[int]
        unknown_four_hundred_sixty_three: int
        available_options_by_key: _containers.ScalarMap[str, bool]
        available_option_ids: _containers.RepeatedScalarFieldContainer[int]
        is_enabled: bool
        unknown_four_hundred_sixty_four: str
        unknown_four_hundred_sixty_five: int
        unknown_four_hundred_sixty_six: int
        def __init__(self, unknown_four_hundred_sixty_three: _Optional[int] = ..., available_options_by_key: _Optional[_Mapping[str, bool]] = ..., available_option_ids: _Optional[_Iterable[int]] = ..., is_enabled: bool = ..., unknown_four_hundred_sixty_four: _Optional[str] = ..., unknown_four_hundred_sixty_five: _Optional[int] = ..., unknown_four_hundred_sixty_six: _Optional[int] = ...) -> None: ...
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    configuration: GuildHallConfigurationEvent.GuildHallConfiguration
    def __init__(self, configuration: _Optional[_Union[GuildHallConfigurationEvent.GuildHallConfiguration, _Mapping]] = ...) -> None: ...

class GuildContributionTokenEvent(_message.Message):
    __slots__ = ("guildaton_count",)
    GUILDATON_COUNT_FIELD_NUMBER: _ClassVar[int]
    guildaton_count: int
    def __init__(self, guildaton_count: _Optional[int] = ...) -> None: ...
