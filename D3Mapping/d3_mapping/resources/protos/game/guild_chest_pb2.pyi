from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildChestTabSelectRequest(_message.Message):
    __slots__ = ("tab_number",)
    TAB_NUMBER_FIELD_NUMBER: _ClassVar[int]
    tab_number: int
    def __init__(self, tab_number: _Optional[int] = ...) -> None: ...

class GuildChestTabUpdateRequest(_message.Message):
    __slots__ = ("tab_number", "name", "picto", "drop_type_limitation")
    TAB_NUMBER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTO_FIELD_NUMBER: _ClassVar[int]
    DROP_TYPE_LIMITATION_FIELD_NUMBER: _ClassVar[int]
    tab_number: int
    name: str
    picto: int
    drop_type_limitation: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, tab_number: _Optional[int] = ..., name: _Optional[str] = ..., picto: _Optional[int] = ..., drop_type_limitation: _Optional[_Iterable[int]] = ...) -> None: ...

class GuildChestTabContributionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildChestContributionStartRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildChestContributionStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildChestStructureStartListeningRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildChestStructureStopListeningRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildChestTabContributionsEvent(_message.Message):
    __slots__ = ("contributions",)
    class Contribution(_message.Message):
        __slots__ = ("contributor_id", "contributor_name", "amount")
        CONTRIBUTOR_ID_FIELD_NUMBER: _ClassVar[int]
        CONTRIBUTOR_NAME_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        contributor_id: int
        contributor_name: str
        amount: int
        def __init__(self, contributor_id: _Optional[int] = ..., contributor_name: _Optional[str] = ..., amount: _Optional[int] = ...) -> None: ...
    CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    contributions: _containers.RepeatedCompositeFieldContainer[GuildChestTabContributionsEvent.Contribution]
    def __init__(self, contributions: _Optional[_Iterable[_Union[GuildChestTabContributionsEvent.Contribution, _Mapping]]] = ...) -> None: ...

class GuildChestTabLastContributionDateEvent(_message.Message):
    __slots__ = ("last_contribution_date",)
    LAST_CONTRIBUTION_DATE_FIELD_NUMBER: _ClassVar[int]
    last_contribution_date: int
    def __init__(self, last_contribution_date: _Optional[int] = ...) -> None: ...

class GuildChestTabContributionEvent(_message.Message):
    __slots__ = ("tab_number", "required_amount", "current_amount", "chest_contribution_enrollment_delay", "chest_contribution_delay")
    TAB_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CHEST_CONTRIBUTION_ENROLLMENT_DELAY_FIELD_NUMBER: _ClassVar[int]
    CHEST_CONTRIBUTION_DELAY_FIELD_NUMBER: _ClassVar[int]
    tab_number: int
    required_amount: int
    current_amount: int
    chest_contribution_enrollment_delay: int
    chest_contribution_delay: int
    def __init__(self, tab_number: _Optional[int] = ..., required_amount: _Optional[int] = ..., current_amount: _Optional[int] = ..., chest_contribution_enrollment_delay: _Optional[int] = ..., chest_contribution_delay: _Optional[int] = ...) -> None: ...

class GuildChestCurrentListenersEvent(_message.Message):
    __slots__ = ("players",)
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    players: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, players: _Optional[_Iterable[str]] = ...) -> None: ...

class GuildChestCurrentListenersAddEvent(_message.Message):
    __slots__ = ("players",)
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    players: str
    def __init__(self, players: _Optional[str] = ...) -> None: ...

class GuildChestCurrentListenersRemoveEvent(_message.Message):
    __slots__ = ("players",)
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    players: str
    def __init__(self, players: _Optional[str] = ...) -> None: ...
