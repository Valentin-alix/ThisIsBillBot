from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllianceInvitationRequest(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class AllianceInvitationAnswerRequest(_message.Message):
    __slots__ = ("accepted",)
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    def __init__(self, accepted: bool = ...) -> None: ...

class AllianceKickRequest(_message.Message):
    __slots__ = ("kicked_id",)
    KICKED_ID_FIELD_NUMBER: _ClassVar[int]
    kicked_id: int
    def __init__(self, kicked_id: _Optional[int] = ...) -> None: ...

class AllianceInvitedEvent(_message.Message):
    __slots__ = ("recruiter_name", "alliance_information")
    RECRUITER_NAME_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    recruiter_name: str
    alliance_information: _common_pb2.AllianceInformation
    def __init__(self, recruiter_name: _Optional[str] = ..., alliance_information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ...) -> None: ...

class AllianceInvitationStateRecruiterEvent(_message.Message):
    __slots__ = ("recruited_name", "invitation_state")
    RECRUITED_NAME_FIELD_NUMBER: _ClassVar[int]
    INVITATION_STATE_FIELD_NUMBER: _ClassVar[int]
    recruited_name: str
    invitation_state: _common_pb2.SocialGroupInvitationState
    def __init__(self, recruited_name: _Optional[str] = ..., invitation_state: _Optional[_Union[_common_pb2.SocialGroupInvitationState, str]] = ...) -> None: ...

class AllianceInvitationStateRecruitedEvent(_message.Message):
    __slots__ = ("invitation_state",)
    INVITATION_STATE_FIELD_NUMBER: _ClassVar[int]
    invitation_state: _common_pb2.SocialGroupInvitationState
    def __init__(self, invitation_state: _Optional[_Union[_common_pb2.SocialGroupInvitationState, str]] = ...) -> None: ...

class AllianceMembershipEvent(_message.Message):
    __slots__ = ("alliance_information", "rank_id")
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    alliance_information: _common_pb2.AllianceInformation
    rank_id: int
    def __init__(self, alliance_information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., rank_id: _Optional[int] = ...) -> None: ...

class AllianceJoinedEvent(_message.Message):
    __slots__ = ("alliance_information", "rank_id")
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    alliance_information: _common_pb2.AllianceInformation
    rank_id: int
    def __init__(self, alliance_information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., rank_id: _Optional[int] = ...) -> None: ...

class AllianceMemberLeavingEvent(_message.Message):
    __slots__ = ("kicked", "member_id")
    KICKED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    kicked: bool
    member_id: int
    def __init__(self, kicked: bool = ..., member_id: _Optional[int] = ...) -> None: ...

class AllianceLeftEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceMemberUpdateEvent(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: _common_pb2.AllianceMemberInformation
    def __init__(self, member: _Optional[_Union[_common_pb2.AllianceMemberInformation, _Mapping]] = ...) -> None: ...
