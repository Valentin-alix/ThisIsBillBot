from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildContributionGiveRequest(_message.Message):
    __slots__ = ("token", "unknown_four_hundred_fifty_seven")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_FIFTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    token: int
    unknown_four_hundred_fifty_seven: str
    def __init__(self, token: _Optional[int] = ..., unknown_four_hundred_fifty_seven: _Optional[str] = ...) -> None: ...

class GuildContributionKamasUpdateEvent(_message.Message):
    __slots__ = ("kamas_spent", "unknown_four_hundred_fifty_eight", "unknown_four_hundred_fifty_nine")
    class GuildContributionKamasUpdateType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
        UNKNOWN_1: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
        UNKNOWN_2: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
        UNKNOWN_3: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
        UNKNOWN_4: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
        UNKNOWN_5: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
        UNKNOWN_6: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
        UNKNOWN_7: _ClassVar[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType]
    UNKNOWN: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    UNKNOWN_1: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    UNKNOWN_2: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    UNKNOWN_3: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    UNKNOWN_4: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    UNKNOWN_5: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    UNKNOWN_6: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    UNKNOWN_7: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    KAMAS_SPENT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_FIFTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_FIFTY_NINE_FIELD_NUMBER: _ClassVar[int]
    kamas_spent: int
    unknown_four_hundred_fifty_eight: int
    unknown_four_hundred_fifty_nine: GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType
    def __init__(self, kamas_spent: _Optional[int] = ..., unknown_four_hundred_fifty_eight: _Optional[int] = ..., unknown_four_hundred_fifty_nine: _Optional[_Union[GuildContributionKamasUpdateEvent.GuildContributionKamasUpdateType, str]] = ...) -> None: ...

class GuildContributionStateEvent(_message.Message):
    __slots__ = ("unknown_four_hundred_sixty",)
    UNKNOWN_FOUR_HUNDRED_SIXTY_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_sixty: int
    def __init__(self, unknown_four_hundred_sixty: _Optional[int] = ...) -> None: ...
