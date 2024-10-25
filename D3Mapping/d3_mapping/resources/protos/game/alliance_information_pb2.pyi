import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllianceCreationValidRequest(_message.Message):
    __slots__ = ("alliance_name", "alliance_tag", "alliance_emblem")
    ALLIANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_TAG_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_EMBLEM_FIELD_NUMBER: _ClassVar[int]
    alliance_name: str
    alliance_tag: str
    alliance_emblem: _common_pb2.SocialEmblem
    def __init__(self, alliance_name: _Optional[str] = ..., alliance_tag: _Optional[str] = ..., alliance_emblem: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class AllianceEmblemModificationValidRequest(_message.Message):
    __slots__ = ("alliance_emblem",)
    ALLIANCE_EMBLEM_FIELD_NUMBER: _ClassVar[int]
    alliance_emblem: _common_pb2.SocialEmblem
    def __init__(self, alliance_emblem: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class AllianceNameAndTagModificationValidRequest(_message.Message):
    __slots__ = ("alliance_name", "alliance_tag")
    ALLIANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_TAG_FIELD_NUMBER: _ClassVar[int]
    alliance_name: str
    alliance_tag: str
    def __init__(self, alliance_name: _Optional[str] = ..., alliance_tag: _Optional[str] = ...) -> None: ...

class AllianceModificationValidRequest(_message.Message):
    __slots__ = ("alliance_name", "alliance_tag", "alliance_emblem")
    ALLIANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_TAG_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_EMBLEM_FIELD_NUMBER: _ClassVar[int]
    alliance_name: str
    alliance_tag: str
    alliance_emblem: _common_pb2.SocialEmblem
    def __init__(self, alliance_name: _Optional[str] = ..., alliance_tag: _Optional[str] = ..., alliance_emblem: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...

class AllianceMemberStartWarningOnConnectionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceMemberStopWarningOnConnectionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceCreationStartedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceModificationStartedEvent(_message.Message):
    __slots__ = ("can_change_name", "can_change_tag", "can_change_emblem")
    CAN_CHANGE_NAME_FIELD_NUMBER: _ClassVar[int]
    CAN_CHANGE_TAG_FIELD_NUMBER: _ClassVar[int]
    CAN_CHANGE_EMBLEM_FIELD_NUMBER: _ClassVar[int]
    can_change_name: bool
    can_change_tag: bool
    can_change_emblem: bool
    def __init__(self, can_change_name: bool = ..., can_change_tag: bool = ..., can_change_emblem: bool = ...) -> None: ...

class AllianceCreationResultEvent(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.SocialGroupOperationResult
    def __init__(self, result: _Optional[_Union[_common_pb2.SocialGroupOperationResult, str]] = ...) -> None: ...

class AllianceModificationResultEvent(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.SocialGroupOperationResult
    def __init__(self, result: _Optional[_Union[_common_pb2.SocialGroupOperationResult, str]] = ...) -> None: ...

class AllianceInsiderInformationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceFactsRequest(_message.Message):
    __slots__ = ("alliance_uuid",)
    ALLIANCE_UUID_FIELD_NUMBER: _ClassVar[int]
    alliance_uuid: str
    def __init__(self, alliance_uuid: _Optional[str] = ...) -> None: ...

class AllianceSummaryRequest(_message.Message):
    __slots__ = ("offset", "count", "filter_type", "text_filer", "hide_full_filter", "following_alliance_criteria", "criterion_filter", "sort_type", "sort_descending", "languages_filter", "recruitment_type_filter", "min_player_level_filter", "max_player_level_filter")
    class DirectoryTextFilter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALLIANCE_SEARCH_DEFAULT_FILTER: _ClassVar[AllianceSummaryRequest.DirectoryTextFilter]
        ALLIANCE_SEARCH_NAME_FILTER: _ClassVar[AllianceSummaryRequest.DirectoryTextFilter]
        ALLIANCE_SEARCH_TAG_FILTER: _ClassVar[AllianceSummaryRequest.DirectoryTextFilter]
    ALLIANCE_SEARCH_DEFAULT_FILTER: AllianceSummaryRequest.DirectoryTextFilter
    ALLIANCE_SEARCH_NAME_FILTER: AllianceSummaryRequest.DirectoryTextFilter
    ALLIANCE_SEARCH_TAG_FILTER: AllianceSummaryRequest.DirectoryTextFilter
    class AllianceSummarySort(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SORT_BY_ALLIANCE_NAME: _ClassVar[AllianceSummaryRequest.AllianceSummarySort]
        SORT_BY_ALLIANCE_TAG: _ClassVar[AllianceSummaryRequest.AllianceSummarySort]
        SORT_BY_NB_TERRITORIES: _ClassVar[AllianceSummaryRequest.AllianceSummarySort]
        SORT_BY_ALLIANCE_NB_MEMBERS: _ClassVar[AllianceSummaryRequest.AllianceSummarySort]
    SORT_BY_ALLIANCE_NAME: AllianceSummaryRequest.AllianceSummarySort
    SORT_BY_ALLIANCE_TAG: AllianceSummaryRequest.AllianceSummarySort
    SORT_BY_NB_TERRITORIES: AllianceSummaryRequest.AllianceSummarySort
    SORT_BY_ALLIANCE_NB_MEMBERS: AllianceSummaryRequest.AllianceSummarySort
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    FILTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FILER_FIELD_NUMBER: _ClassVar[int]
    HIDE_FULL_FILTER_FIELD_NUMBER: _ClassVar[int]
    FOLLOWING_ALLIANCE_CRITERIA_FIELD_NUMBER: _ClassVar[int]
    CRITERION_FILTER_FIELD_NUMBER: _ClassVar[int]
    SORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SORT_DESCENDING_FIELD_NUMBER: _ClassVar[int]
    LANGUAGES_FILTER_FIELD_NUMBER: _ClassVar[int]
    RECRUITMENT_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    MIN_PLAYER_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_PLAYER_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    filter_type: AllianceSummaryRequest.DirectoryTextFilter
    text_filer: str
    hide_full_filter: bool
    following_alliance_criteria: bool
    criterion_filter: _containers.RepeatedScalarFieldContainer[int]
    sort_type: AllianceSummaryRequest.AllianceSummarySort
    sort_descending: bool
    languages_filter: _containers.RepeatedScalarFieldContainer[int]
    recruitment_type_filter: _containers.RepeatedScalarFieldContainer[_common_pb2.SocialRecruitmentType]
    min_player_level_filter: int
    max_player_level_filter: int
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ..., filter_type: _Optional[_Union[AllianceSummaryRequest.DirectoryTextFilter, str]] = ..., text_filer: _Optional[str] = ..., hide_full_filter: bool = ..., following_alliance_criteria: bool = ..., criterion_filter: _Optional[_Iterable[int]] = ..., sort_type: _Optional[_Union[AllianceSummaryRequest.AllianceSummarySort, str]] = ..., sort_descending: bool = ..., languages_filter: _Optional[_Iterable[int]] = ..., recruitment_type_filter: _Optional[_Iterable[_Union[_common_pb2.SocialRecruitmentType, str]]] = ..., min_player_level_filter: _Optional[int] = ..., max_player_level_filter: _Optional[int] = ...) -> None: ...

class AllianceInsiderInformationEvent(_message.Message):
    __slots__ = ("information", "members", "prisms", "tax_collectors")
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    PRISMS_FIELD_NUMBER: _ClassVar[int]
    TAX_COLLECTORS_FIELD_NUMBER: _ClassVar[int]
    information: _common_pb2.AllianceInformation
    members: _containers.RepeatedCompositeFieldContainer[_common_pb2.AllianceMemberInformation]
    prisms: _containers.RepeatedCompositeFieldContainer[_common_pb2.PrismLocalizedInformation]
    tax_collectors: _containers.RepeatedCompositeFieldContainer[_common_pb2.TaxCollectorInformation]
    def __init__(self, information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., members: _Optional[_Iterable[_Union[_common_pb2.AllianceMemberInformation, _Mapping]]] = ..., prisms: _Optional[_Iterable[_Union[_common_pb2.PrismLocalizedInformation, _Mapping]]] = ..., tax_collectors: _Optional[_Iterable[_Union[_common_pb2.TaxCollectorInformation, _Mapping]]] = ...) -> None: ...

class AllianceFactsErrorEvent(_message.Message):
    __slots__ = ("alliance_uuid",)
    ALLIANCE_UUID_FIELD_NUMBER: _ClassVar[int]
    alliance_uuid: str
    def __init__(self, alliance_uuid: _Optional[str] = ...) -> None: ...

class AllianceFactsEvent(_message.Message):
    __slots__ = ("alliance_information", "members", "controlled_subarea_ids", "leader_id", "leader_name")
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    CONTROLLED_SUBAREA_IDS_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    LEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    alliance_information: _common_pb2.AllianceInformation
    members: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    controlled_subarea_ids: _containers.RepeatedScalarFieldContainer[int]
    leader_id: int
    leader_name: str
    def __init__(self, alliance_information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., members: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ..., controlled_subarea_ids: _Optional[_Iterable[int]] = ..., leader_id: _Optional[int] = ..., leader_name: _Optional[str] = ...) -> None: ...

class AllianceSummaryEvent(_message.Message):
    __slots__ = ("offset", "count", "total", "alliances")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    ALLIANCES_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    total: int
    alliances: _containers.RepeatedCompositeFieldContainer[_common_pb2.AllianceInformation]
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ..., total: _Optional[int] = ..., alliances: _Optional[_Iterable[_Union[_common_pb2.AllianceInformation, _Mapping]]] = ...) -> None: ...

class AllianceMotdSetRequest(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class AllianceMotdEvent(_message.Message):
    __slots__ = ("motd_info",)
    MOTD_INFO_FIELD_NUMBER: _ClassVar[int]
    motd_info: _common_pb2.SocialNoticeInformation
    def __init__(self, motd_info: _Optional[_Union[_common_pb2.SocialNoticeInformation, _Mapping]] = ...) -> None: ...

class AllianceMotdSetErrorEvent(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: _common_pb2.SocialNoticeError
    def __init__(self, reason: _Optional[_Union[_common_pb2.SocialNoticeError, str]] = ...) -> None: ...

class AllianceBulletinSetRequest(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class AllianceBulletinEvent(_message.Message):
    __slots__ = ("bulletin_info",)
    BULLETIN_INFO_FIELD_NUMBER: _ClassVar[int]
    bulletin_info: _common_pb2.SocialNoticeInformation
    def __init__(self, bulletin_info: _Optional[_Union[_common_pb2.SocialNoticeInformation, _Mapping]] = ...) -> None: ...

class AllianceBulletinSetErrorEvent(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: _common_pb2.SocialNoticeError
    def __init__(self, reason: _Optional[_Union[_common_pb2.SocialNoticeError, str]] = ...) -> None: ...
