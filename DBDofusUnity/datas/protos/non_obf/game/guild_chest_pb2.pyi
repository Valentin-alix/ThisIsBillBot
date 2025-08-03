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

class UnknownJgs(_message.Message):
    __slots__ = ("unknown_ftgm", "unknown_ftgn")
    UNKNOWN_FTGM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTGN_FIELD_NUMBER: _ClassVar[int]
    unknown_ftgm: _containers.RepeatedScalarFieldContainer[int]
    unknown_ftgn: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_ftgm: _Optional[_Iterable[int]] = ..., unknown_ftgn: _Optional[_Iterable[int]] = ...) -> None: ...

class UnknownJgg(_message.Message):
    __slots__ = ("unknown_ftfd",)
    UNKNOWN_FTFD_FIELD_NUMBER: _ClassVar[int]
    unknown_ftfd: UnknownJgs
    def __init__(self, unknown_ftfd: _Optional[_Union[UnknownJgs, _Mapping]] = ...) -> None: ...

class UnknownJgl(_message.Message):
    __slots__ = ("unknown_ftfp", "unknown_ftfq")
    class UnknownJgi(_message.Message):
        __slots__ = ("unknown_ftfi",)
        UNKNOWN_FTFI_FIELD_NUMBER: _ClassVar[int]
        unknown_ftfi: UnknownJgs
        def __init__(self, unknown_ftfi: _Optional[_Union[UnknownJgs, _Mapping]] = ...) -> None: ...
    UNKNOWN_FTFP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTFQ_FIELD_NUMBER: _ClassVar[int]
    unknown_ftfp: int
    unknown_ftfq: UnknownJgl.UnknownJgi
    def __init__(self, unknown_ftfp: _Optional[int] = ..., unknown_ftfq: _Optional[_Union[UnknownJgl.UnknownJgi, _Mapping]] = ...) -> None: ...

class UnknownJgq(_message.Message):
    __slots__ = ("unknown_ftgd", "unknown_ftge")
    class UnknownJgn(_message.Message):
        __slots__ = ("unknown_ftfv",)
        UNKNOWN_FTFV_FIELD_NUMBER: _ClassVar[int]
        unknown_ftfv: UnknownJgs
        def __init__(self, unknown_ftfv: _Optional[_Union[UnknownJgs, _Mapping]] = ...) -> None: ...
    UNKNOWN_FTGD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTGE_FIELD_NUMBER: _ClassVar[int]
    unknown_ftgd: int
    unknown_ftge: UnknownJgq.UnknownJgn
    def __init__(self, unknown_ftgd: _Optional[int] = ..., unknown_ftge: _Optional[_Union[UnknownJgq.UnknownJgn, _Mapping]] = ...) -> None: ...
