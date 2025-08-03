from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildHallConfigurationEvent(_message.Message):
    __slots__ = ("configuration",)
    class GuildHallConfiguration(_message.Message):
        __slots__ = ("unknown_ftpj", "available_options_by_key", "available_option_ids", "is_enabled", "unknown_ftpn", "unknown_ftpp", "unknown_ftpr")
        class AvailableOptionsByKeyEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: bool
            def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
        UNKNOWN_FTPJ_FIELD_NUMBER: _ClassVar[int]
        AVAILABLE_OPTIONS_BY_KEY_FIELD_NUMBER: _ClassVar[int]
        AVAILABLE_OPTION_IDS_FIELD_NUMBER: _ClassVar[int]
        IS_ENABLED_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FTPN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FTPP_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FTPR_FIELD_NUMBER: _ClassVar[int]
        unknown_ftpj: int
        available_options_by_key: _containers.ScalarMap[str, bool]
        available_option_ids: _containers.RepeatedScalarFieldContainer[int]
        is_enabled: bool
        unknown_ftpn: str
        unknown_ftpp: int
        unknown_ftpr: int
        def __init__(self, unknown_ftpj: _Optional[int] = ..., available_options_by_key: _Optional[_Mapping[str, bool]] = ..., available_option_ids: _Optional[_Iterable[int]] = ..., is_enabled: bool = ..., unknown_ftpn: _Optional[str] = ..., unknown_ftpp: _Optional[int] = ..., unknown_ftpr: _Optional[int] = ...) -> None: ...
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    configuration: GuildHallConfigurationEvent.GuildHallConfiguration
    def __init__(self, configuration: _Optional[_Union[GuildHallConfigurationEvent.GuildHallConfiguration, _Mapping]] = ...) -> None: ...
