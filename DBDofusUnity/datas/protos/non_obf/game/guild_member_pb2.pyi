import common_pb2 as _common_pb2
import guild_member_shop_pb2 as _guild_member_shop_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildMemberParametersChangeRequest(_message.Message):
    __slots__ = ("member_id", "rank_id", "experience_given_percent")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_GIVEN_PERCENT_FIELD_NUMBER: _ClassVar[int]
    member_id: int
    rank_id: int
    experience_given_percent: int
    def __init__(self, member_id: _Optional[int] = ..., rank_id: _Optional[int] = ..., experience_given_percent: _Optional[int] = ...) -> None: ...

class GuildMemberWarnOnConnectionStartRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMemberWarnOnConnectionStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMemberWarnOnConnectionSetRequest(_message.Message):
    __slots__ = ("enable", "guild_id")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    GUILD_ID_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    guild_id: str
    def __init__(self, enable: bool = ..., guild_id: _Optional[str] = ...) -> None: ...

class GuildMemberOnlineStatusEvent(_message.Message):
    __slots__ = ("member_id", "online")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    member_id: int
    online: bool
    def __init__(self, member_id: _Optional[int] = ..., online: bool = ...) -> None: ...

class GuildMembersEvent(_message.Message):
    __slots__ = ("members",)
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    def __init__(self, members: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ...) -> None: ...

class GuildMemberUpdateEvent(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: _common_pb2.Character
    def __init__(self, member: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...

class GuildMemberLeaveEvent(_message.Message):
    __slots__ = ("kicked", "player_id")
    KICKED_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    kicked: bool
    player_id: int
    def __init__(self, kicked: bool = ..., player_id: _Optional[int] = ...) -> None: ...

class GuildLeftEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMembershipEvent(_message.Message):
    __slots__ = ("guild_information", "rank_id", "guildaton_count", "unknown_four_hundred_seventy_one")
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    GUILDATON_COUNT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SEVENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    guild_information: _common_pb2.GuildInformation
    rank_id: int
    guildaton_count: int
    unknown_four_hundred_seventy_one: int
    def __init__(self, guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., rank_id: _Optional[int] = ..., guildaton_count: _Optional[int] = ..., unknown_four_hundred_seventy_one: _Optional[int] = ...) -> None: ...

class GuildJoinedEvent(_message.Message):
    __slots__ = ("guild_information", "rank_id")
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    guild_information: _common_pb2.GuildInformation
    rank_id: int
    def __init__(self, guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., rank_id: _Optional[int] = ...) -> None: ...

class UnknownTwoHundredForty(_message.Message):
    __slots__ = ("unknown_four_hundred_seventy_four", "unknown_four_hundred_seventy_five")
    class UnknownTwoHundredFortyOne(_message.Message):
        __slots__ = ("unknown_four_hundred_seventy_two", "unknown_four_hundred_seventy_three")
        class UnknownFourHundredSeventyThreeEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: UnknownTwoHundredFortyTwo
            def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownTwoHundredFortyTwo, _Mapping]] = ...) -> None: ...
        UNKNOWN_FOUR_HUNDRED_SEVENTY_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_SEVENTY_THREE_FIELD_NUMBER: _ClassVar[int]
        unknown_four_hundred_seventy_two: int
        unknown_four_hundred_seventy_three: _containers.MessageMap[int, UnknownTwoHundredFortyTwo]
        def __init__(self, unknown_four_hundred_seventy_two: _Optional[int] = ..., unknown_four_hundred_seventy_three: _Optional[_Mapping[int, UnknownTwoHundredFortyTwo]] = ...) -> None: ...
    UNKNOWN_FOUR_HUNDRED_SEVENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SEVENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_seventy_four: int
    unknown_four_hundred_seventy_five: UnknownTwoHundredForty.UnknownTwoHundredFortyOne
    def __init__(self, unknown_four_hundred_seventy_four: _Optional[int] = ..., unknown_four_hundred_seventy_five: _Optional[_Union[UnknownTwoHundredForty.UnknownTwoHundredFortyOne, _Mapping]] = ...) -> None: ...

class UnknownTwoHundredFortyTwo(_message.Message):
    __slots__ = ("unknown_four_hundred_seventy_six", "unknown_four_hundred_seventy_seven")
    UNKNOWN_FOUR_HUNDRED_SEVENTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SEVENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_seventy_six: int
    unknown_four_hundred_seventy_seven: _guild_member_shop_pb2.UnknownTwoHundredFortySix
    def __init__(self, unknown_four_hundred_seventy_six: _Optional[int] = ..., unknown_four_hundred_seventy_seven: _Optional[_Union[_guild_member_shop_pb2.UnknownTwoHundredFortySix, _Mapping]] = ...) -> None: ...

class UnknownTwoHundredFortyThree(_message.Message):
    __slots__ = ("unknown_four_hundred_seventy_eight", "unknown_four_hundred_seventy_nine")
    UNKNOWN_FOUR_HUNDRED_SEVENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_SEVENTY_NINE_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_seventy_eight: _guild_member_shop_pb2.UnknownTwoHundredFortySix
    unknown_four_hundred_seventy_nine: int
    def __init__(self, unknown_four_hundred_seventy_eight: _Optional[_Union[_guild_member_shop_pb2.UnknownTwoHundredFortySix, _Mapping]] = ..., unknown_four_hundred_seventy_nine: _Optional[int] = ...) -> None: ...

class UnknownTwoHundredFortyFour(_message.Message):
    __slots__ = ("unknown_four_hundred_eighty",)
    UNKNOWN_FOUR_HUNDRED_EIGHTY_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_eighty: int
    def __init__(self, unknown_four_hundred_eighty: _Optional[int] = ...) -> None: ...

class UnknownTwoHundredFortyFive(_message.Message):
    __slots__ = ("unknown_four_hundred_eighty_one",)
    UNKNOWN_FOUR_HUNDRED_EIGHTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_eighty_one: int
    def __init__(self, unknown_four_hundred_eighty_one: _Optional[int] = ...) -> None: ...
