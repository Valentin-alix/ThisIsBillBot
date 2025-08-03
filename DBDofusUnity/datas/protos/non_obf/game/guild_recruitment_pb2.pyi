import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildRecruitmentUpdateRequest(_message.Message):
    __slots__ = ("recruitment",)
    RECRUITMENT_FIELD_NUMBER: _ClassVar[int]
    recruitment: _common_pb2.GuildRecruitmentInformation
    def __init__(self, recruitment: _Optional[_Union[_common_pb2.GuildRecruitmentInformation, _Mapping]] = ...) -> None: ...

class GuildRecruitmentEvent(_message.Message):
    __slots__ = ("recruitment",)
    RECRUITMENT_FIELD_NUMBER: _ClassVar[int]
    recruitment: _common_pb2.GuildRecruitmentInformation
    def __init__(self, recruitment: _Optional[_Union[_common_pb2.GuildRecruitmentInformation, _Mapping]] = ...) -> None: ...

class GuildRecruitmentInvalidateEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
