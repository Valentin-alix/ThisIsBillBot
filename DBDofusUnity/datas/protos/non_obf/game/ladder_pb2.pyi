import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LadderCharacter(_message.Message):
    __slots__ = ("server_id", "breed_id", "player_name", "gender", "level", "unknown_fqqb")
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQQB_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    breed_id: int
    player_name: str
    gender: _common_pb2.Gender
    level: int
    unknown_fqqb: int
    def __init__(self, server_id: _Optional[int] = ..., breed_id: _Optional[int] = ..., player_name: _Optional[str] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ..., level: _Optional[int] = ..., unknown_fqqb: _Optional[int] = ...) -> None: ...
