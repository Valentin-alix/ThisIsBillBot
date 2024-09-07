from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SpellVariantActivationRequest(_message.Message):
    __slots__ = ("spell_id",)
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    def __init__(self, spell_id: _Optional[int] = ...) -> None: ...

class ForgettableSpellActionRequest(_message.Message):
    __slots__ = ("spell_id", "action")
    class ForgettableSpellAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORGET: _ClassVar[ForgettableSpellActionRequest.ForgettableSpellAction]
        EQUIP: _ClassVar[ForgettableSpellActionRequest.ForgettableSpellAction]
        REMOVE: _ClassVar[ForgettableSpellActionRequest.ForgettableSpellAction]
    FORGET: ForgettableSpellActionRequest.ForgettableSpellAction
    EQUIP: ForgettableSpellActionRequest.ForgettableSpellAction
    REMOVE: ForgettableSpellActionRequest.ForgettableSpellAction
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    action: ForgettableSpellActionRequest.ForgettableSpellAction
    def __init__(self, spell_id: _Optional[int] = ..., action: _Optional[_Union[ForgettableSpellActionRequest.ForgettableSpellAction, str]] = ...) -> None: ...

class ApplySpellModifierEvent(_message.Message):
    __slots__ = ("actor_id", "modifier")
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    MODIFIER_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    modifier: _common_pb2.SpellModifier
    def __init__(self, actor_id: _Optional[int] = ..., modifier: _Optional[_Union[_common_pb2.SpellModifier, _Mapping]] = ...) -> None: ...

class RemoveSpellModifierEvent(_message.Message):
    __slots__ = ("actor_id", "action_type", "modifier_type", "spell_id")
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODIFIER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    action_type: _common_pb2.SpellModifierActionType
    modifier_type: _common_pb2.SpellModifierType
    spell_id: int
    def __init__(self, actor_id: _Optional[int] = ..., action_type: _Optional[_Union[_common_pb2.SpellModifierActionType, str]] = ..., modifier_type: _Optional[_Union[_common_pb2.SpellModifierType, str]] = ..., spell_id: _Optional[int] = ...) -> None: ...

class SpellVariantActivationEvent(_message.Message):
    __slots__ = ("spell_id", "effective")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    effective: bool
    def __init__(self, spell_id: _Optional[int] = ..., effective: bool = ...) -> None: ...

class ForgettableSpellEquipmentSlotsEvent(_message.Message):
    __slots__ = ("quantity",)
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    def __init__(self, quantity: _Optional[int] = ...) -> None: ...

class ForgettableSpellDeletionEvent(_message.Message):
    __slots__ = ("reason", "spells")
    class DeletionReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ForgettableSpellDeletionEvent.DeletionReason]
        ADMIN_COMMAND_REQUEST: _ClassVar[ForgettableSpellDeletionEvent.DeletionReason]
        FORGOTTEN: _ClassVar[ForgettableSpellDeletionEvent.DeletionReason]
        DISABLED: _ClassVar[ForgettableSpellDeletionEvent.DeletionReason]
        NOT_FOUND: _ClassVar[ForgettableSpellDeletionEvent.DeletionReason]
    UNKNOWN: ForgettableSpellDeletionEvent.DeletionReason
    ADMIN_COMMAND_REQUEST: ForgettableSpellDeletionEvent.DeletionReason
    FORGOTTEN: ForgettableSpellDeletionEvent.DeletionReason
    DISABLED: ForgettableSpellDeletionEvent.DeletionReason
    NOT_FOUND: ForgettableSpellDeletionEvent.DeletionReason
    REASON_FIELD_NUMBER: _ClassVar[int]
    SPELLS_FIELD_NUMBER: _ClassVar[int]
    reason: ForgettableSpellDeletionEvent.DeletionReason
    spells: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, reason: _Optional[_Union[ForgettableSpellDeletionEvent.DeletionReason, str]] = ..., spells: _Optional[_Iterable[int]] = ...) -> None: ...

class ForgettableSpellsEvent(_message.Message):
    __slots__ = ("action", "spells")
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISPATCH: _ClassVar[ForgettableSpellsEvent.Action]
        UPDATE: _ClassVar[ForgettableSpellsEvent.Action]
    DISPATCH: ForgettableSpellsEvent.Action
    UPDATE: ForgettableSpellsEvent.Action
    ACTION_FIELD_NUMBER: _ClassVar[int]
    SPELLS_FIELD_NUMBER: _ClassVar[int]
    action: ForgettableSpellsEvent.Action
    spells: _containers.RepeatedCompositeFieldContainer[SpellItem]
    def __init__(self, action: _Optional[_Union[ForgettableSpellsEvent.Action, str]] = ..., spells: _Optional[_Iterable[_Union[SpellItem, _Mapping]]] = ...) -> None: ...

class SpellsEvent(_message.Message):
    __slots__ = ("spell_visualisation", "human_spells", "mutant_spells")
    SPELL_VISUALISATION_FIELD_NUMBER: _ClassVar[int]
    HUMAN_SPELLS_FIELD_NUMBER: _ClassVar[int]
    MUTANT_SPELLS_FIELD_NUMBER: _ClassVar[int]
    spell_visualisation: bool
    human_spells: _containers.RepeatedCompositeFieldContainer[SpellItem]
    mutant_spells: _containers.RepeatedCompositeFieldContainer[SpellItem]
    def __init__(self, spell_visualisation: bool = ..., human_spells: _Optional[_Iterable[_Union[SpellItem, _Mapping]]] = ..., mutant_spells: _Optional[_Iterable[_Union[SpellItem, _Mapping]]] = ...) -> None: ...

class SpellItem(_message.Message):
    __slots__ = ("spell_id", "spell_level", "available")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    SPELL_LEVEL_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    spell_level: int
    available: bool
    def __init__(self, spell_id: _Optional[int] = ..., spell_level: _Optional[int] = ..., available: bool = ...) -> None: ...
