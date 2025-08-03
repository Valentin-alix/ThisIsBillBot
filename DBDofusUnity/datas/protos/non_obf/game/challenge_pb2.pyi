import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChallengeTargetsRequest(_message.Message):
    __slots__ = ("challenge_id",)
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    challenge_id: int
    def __init__(self, challenge_id: _Optional[int] = ...) -> None: ...

class ChallengeSelectionRequest(_message.Message):
    __slots__ = ("challenge_id",)
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    challenge_id: int
    def __init__(self, challenge_id: _Optional[int] = ...) -> None: ...

class ChallengeValidateRequest(_message.Message):
    __slots__ = ("challenge_id",)
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    challenge_id: int
    def __init__(self, challenge_id: _Optional[int] = ...) -> None: ...

class ChallengeModSelectRequest(_message.Message):
    __slots__ = ("challenge_mod",)
    CHALLENGE_MOD_FIELD_NUMBER: _ClassVar[int]
    challenge_mod: _common_pb2.ChallengeMod
    def __init__(self, challenge_mod: _Optional[_Union[_common_pb2.ChallengeMod, str]] = ...) -> None: ...

class ChallengeReadyRequest(_message.Message):
    __slots__ = ("challenge_mod",)
    CHALLENGE_MOD_FIELD_NUMBER: _ClassVar[int]
    challenge_mod: _common_pb2.ChallengeMod
    def __init__(self, challenge_mod: _Optional[_Union[_common_pb2.ChallengeMod, str]] = ...) -> None: ...

class ChallengeBonusChoiceRequest(_message.Message):
    __slots__ = ("challenge_bonus",)
    CHALLENGE_BONUS_FIELD_NUMBER: _ClassVar[int]
    challenge_bonus: _common_pb2.ChallengeBonus
    def __init__(self, challenge_bonus: _Optional[_Union[_common_pb2.ChallengeBonus, str]] = ...) -> None: ...

class ChallengeListEvent(_message.Message):
    __slots__ = ("challenges",)
    CHALLENGES_FIELD_NUMBER: _ClassVar[int]
    challenges: _containers.RepeatedCompositeFieldContainer[_common_pb2.Challenge]
    def __init__(self, challenges: _Optional[_Iterable[_Union[_common_pb2.Challenge, _Mapping]]] = ...) -> None: ...

class ChallengeTargetsEvent(_message.Message):
    __slots__ = ("challenge",)
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    challenge: _common_pb2.Challenge
    def __init__(self, challenge: _Optional[_Union[_common_pb2.Challenge, _Mapping]] = ...) -> None: ...

class ChallengeResultEvent(_message.Message):
    __slots__ = ("challenge_id", "success")
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    challenge_id: int
    success: bool
    def __init__(self, challenge_id: _Optional[int] = ..., success: bool = ...) -> None: ...

class ChallengeNumberEvent(_message.Message):
    __slots__ = ("challenge_number",)
    CHALLENGE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    challenge_number: int
    def __init__(self, challenge_number: _Optional[int] = ...) -> None: ...

class ChallengeProposalEvent(_message.Message):
    __slots__ = ("challenge_proposals", "timer")
    CHALLENGE_PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    TIMER_FIELD_NUMBER: _ClassVar[int]
    challenge_proposals: _containers.RepeatedCompositeFieldContainer[_common_pb2.Challenge]
    timer: int
    def __init__(self, challenge_proposals: _Optional[_Iterable[_Union[_common_pb2.Challenge, _Mapping]]] = ..., timer: _Optional[int] = ...) -> None: ...

class ChallengeSelectedEvent(_message.Message):
    __slots__ = ("challenge",)
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    challenge: _common_pb2.Challenge
    def __init__(self, challenge: _Optional[_Union[_common_pb2.Challenge, _Mapping]] = ...) -> None: ...

class ChallengeAddEvent(_message.Message):
    __slots__ = ("challenge",)
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    challenge: _common_pb2.Challenge
    def __init__(self, challenge: _Optional[_Union[_common_pb2.Challenge, _Mapping]] = ...) -> None: ...

class ChallengeModSelectedEvent(_message.Message):
    __slots__ = ("challenge_mod",)
    CHALLENGE_MOD_FIELD_NUMBER: _ClassVar[int]
    challenge_mod: _common_pb2.ChallengeMod
    def __init__(self, challenge_mod: _Optional[_Union[_common_pb2.ChallengeMod, str]] = ...) -> None: ...

class ChallengeBonusChoiceSelectedEvent(_message.Message):
    __slots__ = ("challenge_bonus",)
    CHALLENGE_BONUS_FIELD_NUMBER: _ClassVar[int]
    challenge_bonus: _common_pb2.ChallengeBonus
    def __init__(self, challenge_bonus: _Optional[_Union[_common_pb2.ChallengeBonus, str]] = ...) -> None: ...
