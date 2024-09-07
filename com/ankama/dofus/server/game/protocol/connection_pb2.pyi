from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class IdentificationRequest(_message.Message):
    __slots__ = ("ticket_key", "language_code")
    TICKET_KEY_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_CODE_FIELD_NUMBER: _ClassVar[int]
    ticket_key: str
    language_code: str
    def __init__(self, ticket_key: _Optional[str] = ..., language_code: _Optional[str] = ...) -> None: ...

class ReloginRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PingRequest(_message.Message):
    __slots__ = ("quiet",)
    QUIET_FIELD_NUMBER: _ClassVar[int]
    quiet: bool
    def __init__(self, quiet: bool = ...) -> None: ...

class PongEvent(_message.Message):
    __slots__ = ("quiet",)
    QUIET_FIELD_NUMBER: _ClassVar[int]
    quiet: bool
    def __init__(self, quiet: bool = ...) -> None: ...

class AuthenticationTicketAcceptedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AlreadyConnectedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReconnectToGameServerEvent(_message.Message):
    __slots__ = ("valid_token", "token", "server_id")
    VALID_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    valid_token: bool
    token: str
    server_id: int
    def __init__(self, valid_token: bool = ..., token: _Optional[str] = ..., server_id: _Optional[int] = ...) -> None: ...

class OptionalFeaturesEvent(_message.Message):
    __slots__ = ("features",)
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    features: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, features: _Optional[_Iterable[int]] = ...) -> None: ...

class ReloginTokenEvent(_message.Message):
    __slots__ = ("valid_token", "token")
    VALID_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    valid_token: bool
    token: str
    def __init__(self, valid_token: bool = ..., token: _Optional[str] = ...) -> None: ...

class QueueStatusEvent(_message.Message):
    __slots__ = ("position", "total")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    position: int
    total: int
    def __init__(self, position: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class AuthenticationTicketRefusedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
