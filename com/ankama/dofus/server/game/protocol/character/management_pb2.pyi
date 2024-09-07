from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PrepareCharacterDeletionRequest(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class CharacterDeletionRequest(_message.Message):
    __slots__ = ("character_id", "secret_answer_hash")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ANSWER_HASH_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    secret_answer_hash: str
    def __init__(self, character_id: _Optional[int] = ..., secret_answer_hash: _Optional[str] = ...) -> None: ...

class CanCreateCharacterRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterCreationRequest(_message.Message):
    __slots__ = ("modelingInformation",)
    MODELINGINFORMATION_FIELD_NUMBER: _ClassVar[int]
    modelingInformation: _common_pb2.CharacterRemodelingInformation
    def __init__(self, modelingInformation: _Optional[_Union[_common_pb2.CharacterRemodelingInformation, _Mapping]] = ...) -> None: ...

class CharacterReplayRequest(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class CharacterReplayWithRemodelRequest(_message.Message):
    __slots__ = ("character_id", "remodelingInformation")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    REMODELINGINFORMATION_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    remodelingInformation: _common_pb2.Character
    def __init__(self, character_id: _Optional[int] = ..., remodelingInformation: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...

class CharacterSelectionRequest(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class CharacterSelectionWithRemodelRequest(_message.Message):
    __slots__ = ("character_id", "remodelingInformation")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    REMODELINGINFORMATION_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    remodelingInformation: _common_pb2.Character
    def __init__(self, character_id: _Optional[int] = ..., remodelingInformation: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...

class CharacterListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterForceSelectionReadyRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterFirstSelectionRequest(_message.Message):
    __slots__ = ("character_id", "do_tutorial")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    DO_TUTORIAL_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    do_tutorial: bool
    def __init__(self, character_id: _Optional[int] = ..., do_tutorial: bool = ...) -> None: ...

class CharacterNameSuggestionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CanCharacterBeCreatedResultEvent(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    def __init__(self, result: bool = ...) -> None: ...

class CharacterCreationResultEvent(_message.Message):
    __slots__ = ("result", "reason")
    class CharacterCreationResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CREATE_OK: _ClassVar[CharacterCreationResultEvent.CharacterCreationResult]
        CREATE_ERROR_NO_REASON: _ClassVar[CharacterCreationResultEvent.CharacterCreationResult]
        CREATE_ERROR_INVALID_NAME: _ClassVar[CharacterCreationResultEvent.CharacterCreationResult]
        CREATE_ERROR_TOO_MANY_CHARACTERS: _ClassVar[CharacterCreationResultEvent.CharacterCreationResult]
        CREATE_ERROR_NOT_ALLOWED: _ClassVar[CharacterCreationResultEvent.CharacterCreationResult]
        CREATE_ERROR_NEW_PLAYER_NOT_ALLOWED: _ClassVar[CharacterCreationResultEvent.CharacterCreationResult]
    CREATE_OK: CharacterCreationResultEvent.CharacterCreationResult
    CREATE_ERROR_NO_REASON: CharacterCreationResultEvent.CharacterCreationResult
    CREATE_ERROR_INVALID_NAME: CharacterCreationResultEvent.CharacterCreationResult
    CREATE_ERROR_TOO_MANY_CHARACTERS: CharacterCreationResultEvent.CharacterCreationResult
    CREATE_ERROR_NOT_ALLOWED: CharacterCreationResultEvent.CharacterCreationResult
    CREATE_ERROR_NEW_PLAYER_NOT_ALLOWED: CharacterCreationResultEvent.CharacterCreationResult
    class NameCompliance(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NAME_OK: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_SERVICE_UNAVAILABLE: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_ALREADY_EXISTS: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_BAD_ALPHABET: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_BAD_LENGTH: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_BAD_CHAR: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_INVALID_DASH_POSITION: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_NAME_WITH_BAD_CASE: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_TOO_MANY_CONSECUTIVE_IDENTICAL: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_TOO_MANY_SPECIAL: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_FORBIDDEN: _ClassVar[CharacterCreationResultEvent.NameCompliance]
        NAME_ERROR_RESERVED: _ClassVar[CharacterCreationResultEvent.NameCompliance]
    NAME_OK: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_SERVICE_UNAVAILABLE: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_ALREADY_EXISTS: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_BAD_ALPHABET: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_BAD_LENGTH: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_BAD_CHAR: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_INVALID_DASH_POSITION: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_NAME_WITH_BAD_CASE: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_TOO_MANY_CONSECUTIVE_IDENTICAL: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_TOO_MANY_SPECIAL: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_FORBIDDEN: CharacterCreationResultEvent.NameCompliance
    NAME_ERROR_RESERVED: CharacterCreationResultEvent.NameCompliance
    RESULT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    result: CharacterCreationResultEvent.CharacterCreationResult
    reason: CharacterCreationResultEvent.NameCompliance
    def __init__(self, result: _Optional[_Union[CharacterCreationResultEvent.CharacterCreationResult, str]] = ..., reason: _Optional[_Union[CharacterCreationResultEvent.NameCompliance, str]] = ...) -> None: ...

class CharacterDeletionErrorEvent(_message.Message):
    __slots__ = ("reason",)
    class CharacterDeletionError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DELETE_ERROR_NO_REASON: _ClassVar[CharacterDeletionErrorEvent.CharacterDeletionError]
        DELETE_ERROR_TOO_MANY_CHAR_DELETED: _ClassVar[CharacterDeletionErrorEvent.CharacterDeletionError]
        DELETE_ERROR_BAD_SECRET_ANSWER: _ClassVar[CharacterDeletionErrorEvent.CharacterDeletionError]
    DELETE_ERROR_NO_REASON: CharacterDeletionErrorEvent.CharacterDeletionError
    DELETE_ERROR_TOO_MANY_CHAR_DELETED: CharacterDeletionErrorEvent.CharacterDeletionError
    DELETE_ERROR_BAD_SECRET_ANSWER: CharacterDeletionErrorEvent.CharacterDeletionError
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: CharacterDeletionErrorEvent.CharacterDeletionError
    def __init__(self, reason: _Optional[_Union[CharacterDeletionErrorEvent.CharacterDeletionError, str]] = ...) -> None: ...

class CharacterSelectionEvent(_message.Message):
    __slots__ = ("error", "success")
    class Error(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Success(_message.Message):
        __slots__ = ("character", "collect_stats")
        CHARACTER_FIELD_NUMBER: _ClassVar[int]
        COLLECT_STATS_FIELD_NUMBER: _ClassVar[int]
        character: _common_pb2.Character
        collect_stats: bool
        def __init__(self, character: _Optional[_Union[_common_pb2.Character, _Mapping]] = ..., collect_stats: bool = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: CharacterSelectionEvent.Error
    success: CharacterSelectionEvent.Success
    def __init__(self, error: _Optional[_Union[CharacterSelectionEvent.Error, _Mapping]] = ..., success: _Optional[_Union[CharacterSelectionEvent.Success, _Mapping]] = ...) -> None: ...

class CharacterListWithRemodelingEvent(_message.Message):
    __slots__ = ("characters", "characters_to_remodel")
    CHARACTERS_FIELD_NUMBER: _ClassVar[int]
    CHARACTERS_TO_REMODEL_FIELD_NUMBER: _ClassVar[int]
    characters: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    characters_to_remodel: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    def __init__(self, characters: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ..., characters_to_remodel: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ...) -> None: ...

class CharacterListEvent(_message.Message):
    __slots__ = ("characters",)
    CHARACTERS_FIELD_NUMBER: _ClassVar[int]
    characters: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    def __init__(self, characters: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ...) -> None: ...

class CharacterLoadingCompleteEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterNameSuggestionEvent(_message.Message):
    __slots__ = ("suggestion",)
    SUGGESTION_FIELD_NUMBER: _ClassVar[int]
    suggestion: str
    def __init__(self, suggestion: _Optional[str] = ...) -> None: ...

class CharacterNameGenerationFailedEvent(_message.Message):
    __slots__ = ("reason",)
    class NameGenerationFailureReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NAME_GENERATOR_RETRY_TOO_SHORT: _ClassVar[CharacterNameGenerationFailedEvent.NameGenerationFailureReason]
        NAME_GENERATOR_UNAVAILABLE: _ClassVar[CharacterNameGenerationFailedEvent.NameGenerationFailureReason]
    NAME_GENERATOR_RETRY_TOO_SHORT: CharacterNameGenerationFailedEvent.NameGenerationFailureReason
    NAME_GENERATOR_UNAVAILABLE: CharacterNameGenerationFailedEvent.NameGenerationFailureReason
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: CharacterNameGenerationFailedEvent.NameGenerationFailureReason
    def __init__(self, reason: _Optional[_Union[CharacterNameGenerationFailedEvent.NameGenerationFailureReason, str]] = ...) -> None: ...

class CharacterDeletionPrepareEvent(_message.Message):
    __slots__ = ("character_id", "name", "secret_question", "need_secret_answer")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SECRET_QUESTION_FIELD_NUMBER: _ClassVar[int]
    NEED_SECRET_ANSWER_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    name: str
    secret_question: str
    need_secret_answer: bool
    def __init__(self, character_id: _Optional[int] = ..., name: _Optional[str] = ..., secret_question: _Optional[str] = ..., need_secret_answer: bool = ...) -> None: ...

class CharacterForceSelectionEvent(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class CharacterListErrorEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterCapabilitiesEvent(_message.Message):
    __slots__ = ("guild_emblem_symbol_category",)
    GUILD_EMBLEM_SYMBOL_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    guild_emblem_symbol_category: int
    def __init__(self, guild_emblem_symbol_category: _Optional[int] = ...) -> None: ...

class CharacterChangeBreedRequest(_message.Message):
    __slots__ = ("breed_id", "gender", "colors", "cosmetic_id", "object_id")
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    COLORS_FIELD_NUMBER: _ClassVar[int]
    COSMETIC_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    breed_id: int
    gender: _common_pb2.Gender
    colors: _containers.RepeatedScalarFieldContainer[int]
    cosmetic_id: int
    object_id: int
    def __init__(self, breed_id: _Optional[int] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ..., colors: _Optional[_Iterable[int]] = ..., cosmetic_id: _Optional[int] = ..., object_id: _Optional[int] = ...) -> None: ...
