from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildTokenConfiguration(_message.Message):
    __slots__ = ("guild_token_items", "refresh_interval_milliseconds", "thresholds")
    class GuildTokenThresholds(_message.Message):
        __slots__ = ("unknown_six_hundred_fifty_six", "unknown_six_hundred_fifty_seven", "unknown_six_hundred_fifty_eight", "unknown_six_hundred_fifty_nine")
        UNKNOWN_SIX_HUNDRED_FIFTY_SIX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_HUNDRED_FIFTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_HUNDRED_FIFTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_HUNDRED_FIFTY_NINE_FIELD_NUMBER: _ClassVar[int]
        unknown_six_hundred_fifty_six: int
        unknown_six_hundred_fifty_seven: int
        unknown_six_hundred_fifty_eight: int
        unknown_six_hundred_fifty_nine: int
        def __init__(self, unknown_six_hundred_fifty_six: _Optional[int] = ..., unknown_six_hundred_fifty_seven: _Optional[int] = ..., unknown_six_hundred_fifty_eight: _Optional[int] = ..., unknown_six_hundred_fifty_nine: _Optional[int] = ...) -> None: ...
    class GuildTokenItems(_message.Message):
        __slots__ = ("guildaton_item_id", "unknown_six_hundred_fifty_two", "unknown_six_hundred_fifty_three", "unknown_six_hundred_fifty_four", "guild_token_item_id", "unknown_six_hundred_fifty_five")
        GUILDATON_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_HUNDRED_FIFTY_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_HUNDRED_FIFTY_THREE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_HUNDRED_FIFTY_FOUR_FIELD_NUMBER: _ClassVar[int]
        GUILD_TOKEN_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_HUNDRED_FIFTY_FIVE_FIELD_NUMBER: _ClassVar[int]
        guildaton_item_id: int
        unknown_six_hundred_fifty_two: int
        unknown_six_hundred_fifty_three: int
        unknown_six_hundred_fifty_four: int
        guild_token_item_id: int
        unknown_six_hundred_fifty_five: int
        def __init__(self, guildaton_item_id: _Optional[int] = ..., unknown_six_hundred_fifty_two: _Optional[int] = ..., unknown_six_hundred_fifty_three: _Optional[int] = ..., unknown_six_hundred_fifty_four: _Optional[int] = ..., guild_token_item_id: _Optional[int] = ..., unknown_six_hundred_fifty_five: _Optional[int] = ...) -> None: ...
    GUILD_TOKEN_ITEMS_FIELD_NUMBER: _ClassVar[int]
    REFRESH_INTERVAL_MILLISECONDS_FIELD_NUMBER: _ClassVar[int]
    THRESHOLDS_FIELD_NUMBER: _ClassVar[int]
    guild_token_items: GuildTokenConfiguration.GuildTokenItems
    refresh_interval_milliseconds: int
    thresholds: GuildTokenConfiguration.GuildTokenThresholds
    def __init__(self, guild_token_items: _Optional[_Union[GuildTokenConfiguration.GuildTokenItems, _Mapping]] = ..., refresh_interval_milliseconds: _Optional[int] = ..., thresholds: _Optional[_Union[GuildTokenConfiguration.GuildTokenThresholds, _Mapping]] = ...) -> None: ...

class GuildTokenConfigurationEvent(_message.Message):
    __slots__ = ("configuration",)
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    configuration: GuildTokenConfiguration
    def __init__(self, configuration: _Optional[_Union[GuildTokenConfiguration, _Mapping]] = ...) -> None: ...
