import common_pb2 as _common_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountRoleStatusEvent(_message.Message):
    __slots__ = ("unknown_gfaj", "unknown_gfak", "role")
    class UnknownGfajValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_GFAJ_VALUE_UNSPECIFIED: _ClassVar[AccountRoleStatusEvent.UnknownGfajValue]
    UNKNOWN_GFAJ_VALUE_UNSPECIFIED: AccountRoleStatusEvent.UnknownGfajValue
    UNKNOWN_GFAJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GFAK_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    unknown_gfaj: AccountRoleStatusEvent.UnknownGfajValue
    unknown_gfak: bool
    role: _common_pb2.Hierarchy
    def __init__(self, unknown_gfaj: _Optional[_Union[AccountRoleStatusEvent.UnknownGfajValue, str]] = ..., unknown_gfak: bool = ..., role: _Optional[_Union[_common_pb2.Hierarchy, str]] = ...) -> None: ...

class AccountSecurityFlagsEvent(_message.Message):
    __slots__ = ("security_flags",)
    class SecurityFlags(_message.Message):
        __slots__ = ("unknown_gfap", "unknown_gfaq", "unknown_gfas", "unknown_gfat")
        UNKNOWN_GFAP_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_GFAQ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_GFAS_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_GFAT_FIELD_NUMBER: _ClassVar[int]
        unknown_gfap: bool
        unknown_gfaq: bool
        unknown_gfas: bool
        unknown_gfat: bool
        def __init__(self, unknown_gfap: bool = ..., unknown_gfaq: bool = ..., unknown_gfas: bool = ..., unknown_gfat: bool = ...) -> None: ...
    SECURITY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    security_flags: AccountSecurityFlagsEvent.SecurityFlags
    def __init__(self, security_flags: _Optional[_Union[AccountSecurityFlagsEvent.SecurityFlags, _Mapping]] = ...) -> None: ...

class SessionElapsedDurationEvent(_message.Message):
    __slots__ = ("duration_seconds",)
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    duration_seconds: int
    def __init__(self, duration_seconds: _Optional[int] = ...) -> None: ...
