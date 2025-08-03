from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ServerSessionReadyEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClientIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ServerVerificationEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClientChallengeInitRequest(_message.Message):
    __slots__ = ("challenge_key",)
    CHALLENGE_KEY_FIELD_NUMBER: _ClassVar[int]
    challenge_key: str
    def __init__(self, challenge_key: _Optional[str] = ...) -> None: ...

class ServerChallengeEvent(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class ClientChallengeProofRequest(_message.Message):
    __slots__ = ("proof",)
    PROOF_FIELD_NUMBER: _ClassVar[int]
    proof: str
    def __init__(self, proof: _Optional[str] = ...) -> None: ...
