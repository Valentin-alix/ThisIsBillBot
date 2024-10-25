import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllianceRecruitmentInformationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceRecruitmentUpdateRequest(_message.Message):
    __slots__ = ("information",)
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    information: _common_pb2.AllianceRecruitmentInformation
    def __init__(self, information: _Optional[_Union[_common_pb2.AllianceRecruitmentInformation, _Mapping]] = ...) -> None: ...

class AllianceRecruitmentInformationEvent(_message.Message):
    __slots__ = ("information",)
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    information: _common_pb2.AllianceRecruitmentInformation
    def __init__(self, information: _Optional[_Union[_common_pb2.AllianceRecruitmentInformation, _Mapping]] = ...) -> None: ...

class AllianceRecruitmentAutomaticJoinRequest(_message.Message):
    __slots__ = ("alliance_uid",)
    ALLIANCE_UID_FIELD_NUMBER: _ClassVar[int]
    alliance_uid: str
    def __init__(self, alliance_uid: _Optional[str] = ...) -> None: ...

class AllianceRecruitmentInvalidateEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceApplicationSubmitRequest(_message.Message):
    __slots__ = ("alliance_uid", "text")
    ALLIANCE_UID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    alliance_uid: str
    text: str
    def __init__(self, alliance_uid: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class AllianceApplicationUpdateRequest(_message.Message):
    __slots__ = ("alliance_uid", "text")
    ALLIANCE_UID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    alliance_uid: str
    text: str
    def __init__(self, alliance_uid: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class AllianceApplicationDeletionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceApplicationListenRequest(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: bool
    def __init__(self, state: bool = ...) -> None: ...

class AllianceApplicationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceApplicationListRequest(_message.Message):
    __slots__ = ("offset", "count")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class AllianceApplicationAnswerRequest(_message.Message):
    __slots__ = ("player_id", "accepted")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    accepted: bool
    def __init__(self, player_id: _Optional[int] = ..., accepted: bool = ...) -> None: ...

class AllianceApplicationPresenceRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceApplicationDeletedEvent(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class AllianceApplicationInformationEvent(_message.Message):
    __slots__ = ("alliance", "application_information")
    ALLIANCE_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    alliance: _common_pb2.AllianceInformation
    application_information: _common_pb2.SocialApplicationInformation
    def __init__(self, alliance: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., application_information: _Optional[_Union[_common_pb2.SocialApplicationInformation, _Mapping]] = ...) -> None: ...

class AllianceApplicationNoInformationEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceApplicationResponseEvent(_message.Message):
    __slots__ = ("accepted", "alliance_information")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    alliance_information: _common_pb2.AllianceInformation
    def __init__(self, accepted: bool = ..., alliance_information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ...) -> None: ...

class AllianceApplicationListEvent(_message.Message):
    __slots__ = ("offset", "count", "total", "applies")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    APPLIES_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    total: int
    applies: _containers.RepeatedCompositeFieldContainer[_common_pb2.SocialApplicationInformation]
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ..., total: _Optional[int] = ..., applies: _Optional[_Iterable[_Union[_common_pb2.SocialApplicationInformation, _Mapping]]] = ...) -> None: ...

class AllianceApplicationModifiedEvent(_message.Message):
    __slots__ = ("apply", "state", "player_id")
    APPLY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    apply: _common_pb2.SocialApplicationInformation
    state: _common_pb2.SocialApplicationState
    player_id: int
    def __init__(self, apply: _Optional[_Union[_common_pb2.SocialApplicationInformation, _Mapping]] = ..., state: _Optional[_Union[_common_pb2.SocialApplicationState, str]] = ..., player_id: _Optional[int] = ...) -> None: ...

class AllianceApplicationReceivedEvent(_message.Message):
    __slots__ = ("player_name", "player_id")
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    player_name: str
    player_id: int
    def __init__(self, player_name: _Optional[str] = ..., player_id: _Optional[int] = ...) -> None: ...

class AllianceApplicationPresenceEvent(_message.Message):
    __slots__ = ("presence",)
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    presence: bool
    def __init__(self, presence: bool = ...) -> None: ...
