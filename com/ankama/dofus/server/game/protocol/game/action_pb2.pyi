from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FightSpellCastCritical(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NORMAL: _ClassVar[FightSpellCastCritical]
    CRITICAL_HIT: _ClassVar[FightSpellCastCritical]
    CRITICAL_FAIL: _ClassVar[FightSpellCastCritical]

class SequenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SPELL: _ClassVar[SequenceType]
    WEAPON: _ClassVar[SequenceType]
    GLYPH_TRAP: _ClassVar[SequenceType]
    TRIGGERED: _ClassVar[SequenceType]
    MOVE: _ClassVar[SequenceType]
    CHARACTER_DEATH: _ClassVar[SequenceType]
    TURN_START: _ClassVar[SequenceType]
    TURN_END: _ClassVar[SequenceType]
    FIGHT_START: _ClassVar[SequenceType]
NORMAL: FightSpellCastCritical
CRITICAL_HIT: FightSpellCastCritical
CRITICAL_FAIL: FightSpellCastCritical
SPELL: SequenceType
WEAPON: SequenceType
GLYPH_TRAP: SequenceType
TRIGGERED: SequenceType
MOVE: SequenceType
CHARACTER_DEATH: SequenceType
TURN_START: SequenceType
TURN_END: SequenceType
FIGHT_START: SequenceType

class GameActionItemConsumeRequest(_message.Message):
    __slots__ = ("action_id", "player_id")
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    action_id: int
    player_id: int
    def __init__(self, action_id: _Optional[int] = ..., player_id: _Optional[int] = ...) -> None: ...

class GameActionItemConsumeAllRequest(_message.Message):
    __slots__ = ("player_id",)
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    def __init__(self, player_id: _Optional[int] = ...) -> None: ...

class GameActionFightCastRequest(_message.Message):
    __slots__ = ("spell_id", "cell")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    cell: int
    def __init__(self, spell_id: _Optional[int] = ..., cell: _Optional[int] = ...) -> None: ...

class GameActionFightCastOnTargetRequest(_message.Message):
    __slots__ = ("spell_id", "target_id")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    target_id: int
    def __init__(self, spell_id: _Optional[int] = ..., target_id: _Optional[int] = ...) -> None: ...

class GameActionAcknowledgementRequest(_message.Message):
    __slots__ = ("valid", "action_id")
    VALID_FIELD_NUMBER: _ClassVar[int]
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    action_id: int
    def __init__(self, valid: bool = ..., action_id: _Optional[int] = ...) -> None: ...

class GameActionItemListEvent(_message.Message):
    __slots__ = ("actions",)
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    actions: _containers.RepeatedCompositeFieldContainer[_common_pb2.GameActionItem]
    def __init__(self, actions: _Optional[_Iterable[_Union[_common_pb2.GameActionItem, _Mapping]]] = ...) -> None: ...

class GameActionItemConsumedEvent(_message.Message):
    __slots__ = ("success", "action_id", "automatic_action")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    AUTOMATIC_ACTION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    action_id: int
    automatic_action: bool
    def __init__(self, success: bool = ..., action_id: _Optional[int] = ..., automatic_action: bool = ...) -> None: ...

class GameActionSpamEvent(_message.Message):
    __slots__ = ("cells",)
    CELLS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, cells: _Optional[_Iterable[int]] = ...) -> None: ...

class GameActionFightEvent(_message.Message):
    __slots__ = ("action_id", "source_id", "slide", "dodge_point_loss", "reflect_damages", "reduce_damages", "reflect_spell", "removable_effect", "life_points_lost", "life_points_gain", "spell_immunity", "spell_cool_down_variation", "vanish", "kill", "death", "targeted_ability", "tackled", "points_variation", "invisible_detected", "teleport_on_same_map", "exchange_positions", "spell_remove", "modify_effects_duration", "steal_kama", "change_look", "invisibility", "summons", "mark_cells", "unmark_cells", "trigger_glyph_trap", "activate_glyph_trap", "carry_character", "throw_character", "drop_character", "execute_script")
    class CarryCharacter(_message.Message):
        __slots__ = ("target_id", "cell")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        CELL_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        cell: int
        def __init__(self, target_id: _Optional[int] = ..., cell: _Optional[int] = ...) -> None: ...
    class ThrowCharacter(_message.Message):
        __slots__ = ("target_id", "cell")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        CELL_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        cell: int
        def __init__(self, target_id: _Optional[int] = ..., cell: _Optional[int] = ...) -> None: ...
    class DropCharacter(_message.Message):
        __slots__ = ("target_id", "cell")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        CELL_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        cell: int
        def __init__(self, target_id: _Optional[int] = ..., cell: _Optional[int] = ...) -> None: ...
    class ExecuteScript(_message.Message):
        __slots__ = ("script_usage_id", "critical", "spell_id", "spell_rank", "cell")
        SCRIPT_USAGE_ID_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_FIELD_NUMBER: _ClassVar[int]
        SPELL_ID_FIELD_NUMBER: _ClassVar[int]
        SPELL_RANK_FIELD_NUMBER: _ClassVar[int]
        CELL_FIELD_NUMBER: _ClassVar[int]
        script_usage_id: int
        critical: bool
        spell_id: int
        spell_rank: int
        cell: int
        def __init__(self, script_usage_id: _Optional[int] = ..., critical: bool = ..., spell_id: _Optional[int] = ..., spell_rank: _Optional[int] = ..., cell: _Optional[int] = ...) -> None: ...
    class UnmarkCells(_message.Message):
        __slots__ = ("mark_id",)
        MARK_ID_FIELD_NUMBER: _ClassVar[int]
        mark_id: int
        def __init__(self, mark_id: _Optional[int] = ...) -> None: ...
    class TriggerGlyphTrap(_message.Message):
        __slots__ = ("mark_id", "mark_impact_cell", "triggering_character_id")
        MARK_ID_FIELD_NUMBER: _ClassVar[int]
        MARK_IMPACT_CELL_FIELD_NUMBER: _ClassVar[int]
        TRIGGERING_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
        mark_id: int
        mark_impact_cell: int
        triggering_character_id: int
        def __init__(self, mark_id: _Optional[int] = ..., mark_impact_cell: _Optional[int] = ..., triggering_character_id: _Optional[int] = ...) -> None: ...
    class ActivateGlyphTrap(_message.Message):
        __slots__ = ("mark_id", "active")
        MARK_ID_FIELD_NUMBER: _ClassVar[int]
        ACTIVE_FIELD_NUMBER: _ClassVar[int]
        mark_id: int
        active: bool
        def __init__(self, mark_id: _Optional[int] = ..., active: bool = ...) -> None: ...
    class Invisibility(_message.Message):
        __slots__ = ("target_id", "invisibility_state")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        INVISIBILITY_STATE_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        invisibility_state: _common_pb2.FightInvisibilityState
        def __init__(self, target_id: _Optional[int] = ..., invisibility_state: _Optional[_Union[_common_pb2.FightInvisibilityState, str]] = ...) -> None: ...
    class Summons(_message.Message):
        __slots__ = ("summons_by_actor", "summons_by_context_information")
        class SummonsByActor(_message.Message):
            __slots__ = ("summons",)
            SUMMONS_FIELD_NUMBER: _ClassVar[int]
            summons: _containers.RepeatedCompositeFieldContainer[_common_pb2.ActorPositionInformation]
            def __init__(self, summons: _Optional[_Iterable[_Union[_common_pb2.ActorPositionInformation, _Mapping]]] = ...) -> None: ...
        class SummonsByContextInformation(_message.Message):
            __slots__ = ("summons",)
            class SummonContextInformation(_message.Message):
                __slots__ = ("spawn_information", "wave", "look", "characteristics", "summons")
                SPAWN_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                WAVE_FIELD_NUMBER: _ClassVar[int]
                LOOK_FIELD_NUMBER: _ClassVar[int]
                CHARACTERISTICS_FIELD_NUMBER: _ClassVar[int]
                SUMMONS_FIELD_NUMBER: _ClassVar[int]
                spawn_information: EntitySpawnInformation
                wave: int
                look: _common_pb2.EntityLook
                characteristics: _common_pb2.FightCharacteristics
                summons: _containers.RepeatedCompositeFieldContainer[_common_pb2.SpawnInformation]
                def __init__(self, spawn_information: _Optional[_Union[EntitySpawnInformation, _Mapping]] = ..., wave: _Optional[int] = ..., look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., characteristics: _Optional[_Union[_common_pb2.FightCharacteristics, _Mapping]] = ..., summons: _Optional[_Iterable[_Union[_common_pb2.SpawnInformation, _Mapping]]] = ...) -> None: ...
            SUMMONS_FIELD_NUMBER: _ClassVar[int]
            summons: _containers.RepeatedCompositeFieldContainer[GameActionFightEvent.Summons.SummonsByContextInformation.SummonContextInformation]
            def __init__(self, summons: _Optional[_Iterable[_Union[GameActionFightEvent.Summons.SummonsByContextInformation.SummonContextInformation, _Mapping]]] = ...) -> None: ...
        SUMMONS_BY_ACTOR_FIELD_NUMBER: _ClassVar[int]
        SUMMONS_BY_CONTEXT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        summons_by_actor: GameActionFightEvent.Summons.SummonsByActor
        summons_by_context_information: GameActionFightEvent.Summons.SummonsByContextInformation
        def __init__(self, summons_by_actor: _Optional[_Union[GameActionFightEvent.Summons.SummonsByActor, _Mapping]] = ..., summons_by_context_information: _Optional[_Union[GameActionFightEvent.Summons.SummonsByContextInformation, _Mapping]] = ...) -> None: ...
    class MarkCells(_message.Message):
        __slots__ = ("mark",)
        MARK_FIELD_NUMBER: _ClassVar[int]
        mark: _common_pb2.FightMark
        def __init__(self, mark: _Optional[_Union[_common_pb2.FightMark, _Mapping]] = ...) -> None: ...
    class ModifyEffectsDuration(_message.Message):
        __slots__ = ("target_id", "delta")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        DELTA_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        delta: int
        def __init__(self, target_id: _Optional[int] = ..., delta: _Optional[int] = ...) -> None: ...
    class StealKama(_message.Message):
        __slots__ = ("target_id", "amount")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        amount: int
        def __init__(self, target_id: _Optional[int] = ..., amount: _Optional[int] = ...) -> None: ...
    class ChangeLook(_message.Message):
        __slots__ = ("target_id", "look")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        LOOK_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        look: _common_pb2.EntityLook
        def __init__(self, target_id: _Optional[int] = ..., look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...
    class TeleportOnSameMap(_message.Message):
        __slots__ = ("target_id", "cell")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        CELL_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        cell: int
        def __init__(self, target_id: _Optional[int] = ..., cell: _Optional[int] = ...) -> None: ...
    class ExchangePositions(_message.Message):
        __slots__ = ("target_id", "caster_cell_id", "target_cell_id")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        CASTER_CELL_ID_FIELD_NUMBER: _ClassVar[int]
        TARGET_CELL_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        caster_cell_id: int
        target_cell_id: int
        def __init__(self, target_id: _Optional[int] = ..., caster_cell_id: _Optional[int] = ..., target_cell_id: _Optional[int] = ...) -> None: ...
    class SpellRemove(_message.Message):
        __slots__ = ("target_id", "verbose_cast", "effect_remove", "spell_id")
        class EffectRemove(_message.Message):
            __slots__ = ("effect", "trigger")
            EFFECT_FIELD_NUMBER: _ClassVar[int]
            TRIGGER_FIELD_NUMBER: _ClassVar[int]
            effect: int
            trigger: bool
            def __init__(self, effect: _Optional[int] = ..., trigger: bool = ...) -> None: ...
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        VERBOSE_CAST_FIELD_NUMBER: _ClassVar[int]
        EFFECT_REMOVE_FIELD_NUMBER: _ClassVar[int]
        SPELL_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        verbose_cast: bool
        effect_remove: GameActionFightEvent.SpellRemove.EffectRemove
        spell_id: int
        def __init__(self, target_id: _Optional[int] = ..., verbose_cast: bool = ..., effect_remove: _Optional[_Union[GameActionFightEvent.SpellRemove.EffectRemove, _Mapping]] = ..., spell_id: _Optional[int] = ...) -> None: ...
    class Tackled(_message.Message):
        __slots__ = ("tacklers_id",)
        TACKLERS_ID_FIELD_NUMBER: _ClassVar[int]
        tacklers_id: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, tacklers_id: _Optional[_Iterable[int]] = ...) -> None: ...
    class PointsVariation(_message.Message):
        __slots__ = ("target_id", "delta")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        DELTA_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        delta: int
        def __init__(self, target_id: _Optional[int] = ..., delta: _Optional[int] = ...) -> None: ...
    class InvisibleDetected(_message.Message):
        __slots__ = ("target_id", "cell")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        CELL_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        cell: int
        def __init__(self, target_id: _Optional[int] = ..., cell: _Optional[int] = ...) -> None: ...
    class TargetedAbility(_message.Message):
        __slots__ = ("target_id", "destination_cell", "critical", "silent_cast", "verbose_cast", "spell_cast", "weapon_generic_id")
        class SpellCast(_message.Message):
            __slots__ = ("spell_id", "spell_level", "portals_id")
            SPELL_ID_FIELD_NUMBER: _ClassVar[int]
            SPELL_LEVEL_FIELD_NUMBER: _ClassVar[int]
            PORTALS_ID_FIELD_NUMBER: _ClassVar[int]
            spell_id: int
            spell_level: int
            portals_id: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, spell_id: _Optional[int] = ..., spell_level: _Optional[int] = ..., portals_id: _Optional[_Iterable[int]] = ...) -> None: ...
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        DESTINATION_CELL_FIELD_NUMBER: _ClassVar[int]
        CRITICAL_FIELD_NUMBER: _ClassVar[int]
        SILENT_CAST_FIELD_NUMBER: _ClassVar[int]
        VERBOSE_CAST_FIELD_NUMBER: _ClassVar[int]
        SPELL_CAST_FIELD_NUMBER: _ClassVar[int]
        WEAPON_GENERIC_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        destination_cell: int
        critical: FightSpellCastCritical
        silent_cast: bool
        verbose_cast: bool
        spell_cast: GameActionFightEvent.TargetedAbility.SpellCast
        weapon_generic_id: int
        def __init__(self, target_id: _Optional[int] = ..., destination_cell: _Optional[int] = ..., critical: _Optional[_Union[FightSpellCastCritical, str]] = ..., silent_cast: bool = ..., verbose_cast: bool = ..., spell_cast: _Optional[_Union[GameActionFightEvent.TargetedAbility.SpellCast, _Mapping]] = ..., weapon_generic_id: _Optional[int] = ...) -> None: ...
    class Vanish(_message.Message):
        __slots__ = ("target_id",)
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        def __init__(self, target_id: _Optional[int] = ...) -> None: ...
    class Kill(_message.Message):
        __slots__ = ("target_id",)
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        def __init__(self, target_id: _Optional[int] = ...) -> None: ...
    class Death(_message.Message):
        __slots__ = ("target_id",)
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        def __init__(self, target_id: _Optional[int] = ...) -> None: ...
    class SpellImmunity(_message.Message):
        __slots__ = ("target_id", "spell_id")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        SPELL_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        spell_id: int
        def __init__(self, target_id: _Optional[int] = ..., spell_id: _Optional[int] = ...) -> None: ...
    class SpellCoolDownVariation(_message.Message):
        __slots__ = ("target_id", "spell_id", "value")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        SPELL_ID_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        spell_id: int
        value: int
        def __init__(self, target_id: _Optional[int] = ..., spell_id: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class LifePointsLost(_message.Message):
        __slots__ = ("target_id", "loss", "permanent_damages", "element_id", "shield_loss")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        LOSS_FIELD_NUMBER: _ClassVar[int]
        PERMANENT_DAMAGES_FIELD_NUMBER: _ClassVar[int]
        ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
        SHIELD_LOSS_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        loss: int
        permanent_damages: int
        element_id: int
        shield_loss: int
        def __init__(self, target_id: _Optional[int] = ..., loss: _Optional[int] = ..., permanent_damages: _Optional[int] = ..., element_id: _Optional[int] = ..., shield_loss: _Optional[int] = ...) -> None: ...
    class LifePointsGain(_message.Message):
        __slots__ = ("target_id", "delta")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        DELTA_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        delta: int
        def __init__(self, target_id: _Optional[int] = ..., delta: _Optional[int] = ...) -> None: ...
    class RemovableEffect(_message.Message):
        __slots__ = ("effect",)
        EFFECT_FIELD_NUMBER: _ClassVar[int]
        effect: _common_pb2.FightRemovableEffect
        def __init__(self, effect: _Optional[_Union[_common_pb2.FightRemovableEffect, _Mapping]] = ...) -> None: ...
    class Slide(_message.Message):
        __slots__ = ("target_id", "start_cell", "end_cell")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        START_CELL_FIELD_NUMBER: _ClassVar[int]
        END_CELL_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        start_cell: int
        end_cell: int
        def __init__(self, target_id: _Optional[int] = ..., start_cell: _Optional[int] = ..., end_cell: _Optional[int] = ...) -> None: ...
    class DodgePointLoss(_message.Message):
        __slots__ = ("target_id", "amount")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        amount: int
        def __init__(self, target_id: _Optional[int] = ..., amount: _Optional[int] = ...) -> None: ...
    class ReflectDamages(_message.Message):
        __slots__ = ("target_id",)
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        def __init__(self, target_id: _Optional[int] = ...) -> None: ...
    class ReduceDamages(_message.Message):
        __slots__ = ("target_id", "amount")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        amount: int
        def __init__(self, target_id: _Optional[int] = ..., amount: _Optional[int] = ...) -> None: ...
    class ReflectSpell(_message.Message):
        __slots__ = ("target_id",)
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        def __init__(self, target_id: _Optional[int] = ...) -> None: ...
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    SLIDE_FIELD_NUMBER: _ClassVar[int]
    DODGE_POINT_LOSS_FIELD_NUMBER: _ClassVar[int]
    REFLECT_DAMAGES_FIELD_NUMBER: _ClassVar[int]
    REDUCE_DAMAGES_FIELD_NUMBER: _ClassVar[int]
    REFLECT_SPELL_FIELD_NUMBER: _ClassVar[int]
    REMOVABLE_EFFECT_FIELD_NUMBER: _ClassVar[int]
    LIFE_POINTS_LOST_FIELD_NUMBER: _ClassVar[int]
    LIFE_POINTS_GAIN_FIELD_NUMBER: _ClassVar[int]
    SPELL_IMMUNITY_FIELD_NUMBER: _ClassVar[int]
    SPELL_COOL_DOWN_VARIATION_FIELD_NUMBER: _ClassVar[int]
    VANISH_FIELD_NUMBER: _ClassVar[int]
    KILL_FIELD_NUMBER: _ClassVar[int]
    DEATH_FIELD_NUMBER: _ClassVar[int]
    TARGETED_ABILITY_FIELD_NUMBER: _ClassVar[int]
    TACKLED_FIELD_NUMBER: _ClassVar[int]
    POINTS_VARIATION_FIELD_NUMBER: _ClassVar[int]
    INVISIBLE_DETECTED_FIELD_NUMBER: _ClassVar[int]
    TELEPORT_ON_SAME_MAP_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    SPELL_REMOVE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_EFFECTS_DURATION_FIELD_NUMBER: _ClassVar[int]
    STEAL_KAMA_FIELD_NUMBER: _ClassVar[int]
    CHANGE_LOOK_FIELD_NUMBER: _ClassVar[int]
    INVISIBILITY_FIELD_NUMBER: _ClassVar[int]
    SUMMONS_FIELD_NUMBER: _ClassVar[int]
    MARK_CELLS_FIELD_NUMBER: _ClassVar[int]
    UNMARK_CELLS_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_GLYPH_TRAP_FIELD_NUMBER: _ClassVar[int]
    ACTIVATE_GLYPH_TRAP_FIELD_NUMBER: _ClassVar[int]
    CARRY_CHARACTER_FIELD_NUMBER: _ClassVar[int]
    THROW_CHARACTER_FIELD_NUMBER: _ClassVar[int]
    DROP_CHARACTER_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_SCRIPT_FIELD_NUMBER: _ClassVar[int]
    action_id: int
    source_id: int
    slide: GameActionFightEvent.Slide
    dodge_point_loss: GameActionFightEvent.DodgePointLoss
    reflect_damages: GameActionFightEvent.ReflectDamages
    reduce_damages: GameActionFightEvent.ReduceDamages
    reflect_spell: GameActionFightEvent.ReflectSpell
    removable_effect: GameActionFightEvent.RemovableEffect
    life_points_lost: GameActionFightEvent.LifePointsLost
    life_points_gain: GameActionFightEvent.LifePointsGain
    spell_immunity: GameActionFightEvent.SpellImmunity
    spell_cool_down_variation: GameActionFightEvent.SpellCoolDownVariation
    vanish: GameActionFightEvent.Vanish
    kill: GameActionFightEvent.Kill
    death: GameActionFightEvent.Death
    targeted_ability: GameActionFightEvent.TargetedAbility
    tackled: GameActionFightEvent.Tackled
    points_variation: GameActionFightEvent.PointsVariation
    invisible_detected: GameActionFightEvent.InvisibleDetected
    teleport_on_same_map: GameActionFightEvent.TeleportOnSameMap
    exchange_positions: GameActionFightEvent.ExchangePositions
    spell_remove: GameActionFightEvent.SpellRemove
    modify_effects_duration: GameActionFightEvent.ModifyEffectsDuration
    steal_kama: GameActionFightEvent.StealKama
    change_look: GameActionFightEvent.ChangeLook
    invisibility: GameActionFightEvent.Invisibility
    summons: GameActionFightEvent.Summons
    mark_cells: GameActionFightEvent.MarkCells
    unmark_cells: GameActionFightEvent.UnmarkCells
    trigger_glyph_trap: GameActionFightEvent.TriggerGlyphTrap
    activate_glyph_trap: GameActionFightEvent.ActivateGlyphTrap
    carry_character: GameActionFightEvent.CarryCharacter
    throw_character: GameActionFightEvent.ThrowCharacter
    drop_character: GameActionFightEvent.DropCharacter
    execute_script: GameActionFightEvent.ExecuteScript
    def __init__(self, action_id: _Optional[int] = ..., source_id: _Optional[int] = ..., slide: _Optional[_Union[GameActionFightEvent.Slide, _Mapping]] = ..., dodge_point_loss: _Optional[_Union[GameActionFightEvent.DodgePointLoss, _Mapping]] = ..., reflect_damages: _Optional[_Union[GameActionFightEvent.ReflectDamages, _Mapping]] = ..., reduce_damages: _Optional[_Union[GameActionFightEvent.ReduceDamages, _Mapping]] = ..., reflect_spell: _Optional[_Union[GameActionFightEvent.ReflectSpell, _Mapping]] = ..., removable_effect: _Optional[_Union[GameActionFightEvent.RemovableEffect, _Mapping]] = ..., life_points_lost: _Optional[_Union[GameActionFightEvent.LifePointsLost, _Mapping]] = ..., life_points_gain: _Optional[_Union[GameActionFightEvent.LifePointsGain, _Mapping]] = ..., spell_immunity: _Optional[_Union[GameActionFightEvent.SpellImmunity, _Mapping]] = ..., spell_cool_down_variation: _Optional[_Union[GameActionFightEvent.SpellCoolDownVariation, _Mapping]] = ..., vanish: _Optional[_Union[GameActionFightEvent.Vanish, _Mapping]] = ..., kill: _Optional[_Union[GameActionFightEvent.Kill, _Mapping]] = ..., death: _Optional[_Union[GameActionFightEvent.Death, _Mapping]] = ..., targeted_ability: _Optional[_Union[GameActionFightEvent.TargetedAbility, _Mapping]] = ..., tackled: _Optional[_Union[GameActionFightEvent.Tackled, _Mapping]] = ..., points_variation: _Optional[_Union[GameActionFightEvent.PointsVariation, _Mapping]] = ..., invisible_detected: _Optional[_Union[GameActionFightEvent.InvisibleDetected, _Mapping]] = ..., teleport_on_same_map: _Optional[_Union[GameActionFightEvent.TeleportOnSameMap, _Mapping]] = ..., exchange_positions: _Optional[_Union[GameActionFightEvent.ExchangePositions, _Mapping]] = ..., spell_remove: _Optional[_Union[GameActionFightEvent.SpellRemove, _Mapping]] = ..., modify_effects_duration: _Optional[_Union[GameActionFightEvent.ModifyEffectsDuration, _Mapping]] = ..., steal_kama: _Optional[_Union[GameActionFightEvent.StealKama, _Mapping]] = ..., change_look: _Optional[_Union[GameActionFightEvent.ChangeLook, _Mapping]] = ..., invisibility: _Optional[_Union[GameActionFightEvent.Invisibility, _Mapping]] = ..., summons: _Optional[_Union[GameActionFightEvent.Summons, _Mapping]] = ..., mark_cells: _Optional[_Union[GameActionFightEvent.MarkCells, _Mapping]] = ..., unmark_cells: _Optional[_Union[GameActionFightEvent.UnmarkCells, _Mapping]] = ..., trigger_glyph_trap: _Optional[_Union[GameActionFightEvent.TriggerGlyphTrap, _Mapping]] = ..., activate_glyph_trap: _Optional[_Union[GameActionFightEvent.ActivateGlyphTrap, _Mapping]] = ..., carry_character: _Optional[_Union[GameActionFightEvent.CarryCharacter, _Mapping]] = ..., throw_character: _Optional[_Union[GameActionFightEvent.ThrowCharacter, _Mapping]] = ..., drop_character: _Optional[_Union[GameActionFightEvent.DropCharacter, _Mapping]] = ..., execute_script: _Optional[_Union[GameActionFightEvent.ExecuteScript, _Mapping]] = ...) -> None: ...

class GameActionUpdateEffectTriggerCountEvent(_message.Message):
    __slots__ = ("effects_count_on_target",)
    class FightEffectTriggerCount(_message.Message):
        __slots__ = ("effect_id", "target_id", "count")
        EFFECT_ID_FIELD_NUMBER: _ClassVar[int]
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        effect_id: int
        target_id: int
        count: int
        def __init__(self, effect_id: _Optional[int] = ..., target_id: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...
    EFFECTS_COUNT_ON_TARGET_FIELD_NUMBER: _ClassVar[int]
    effects_count_on_target: _containers.RepeatedCompositeFieldContainer[GameActionUpdateEffectTriggerCountEvent.FightEffectTriggerCount]
    def __init__(self, effects_count_on_target: _Optional[_Iterable[_Union[GameActionUpdateEffectTriggerCountEvent.FightEffectTriggerCount, _Mapping]]] = ...) -> None: ...

class SequenceStartEvent(_message.Message):
    __slots__ = ("sequence_type", "author_id")
    SEQUENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    sequence_type: SequenceType
    author_id: int
    def __init__(self, sequence_type: _Optional[_Union[SequenceType, str]] = ..., author_id: _Optional[int] = ...) -> None: ...

class SequenceEndEvent(_message.Message):
    __slots__ = ("action_id", "author_id", "sequence_type")
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    action_id: int
    author_id: int
    sequence_type: SequenceType
    def __init__(self, action_id: _Optional[int] = ..., author_id: _Optional[int] = ..., sequence_type: _Optional[_Union[SequenceType, str]] = ...) -> None: ...

class EntitySpawnInformation(_message.Message):
    __slots__ = ("monster", "character", "companion")
    class Monster(_message.Message):
        __slots__ = ("monster_gid", "grade", "level")
        MONSTER_GID_FIELD_NUMBER: _ClassVar[int]
        GRADE_FIELD_NUMBER: _ClassVar[int]
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        monster_gid: int
        grade: int
        level: int
        def __init__(self, monster_gid: _Optional[int] = ..., grade: _Optional[int] = ..., level: _Optional[int] = ...) -> None: ...
    class Character(_message.Message):
        __slots__ = ("name", "level")
        NAME_FIELD_NUMBER: _ClassVar[int]
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        name: str
        level: int
        def __init__(self, name: _Optional[str] = ..., level: _Optional[int] = ...) -> None: ...
    class Companion(_message.Message):
        __slots__ = ("model_id", "level", "summoner_id", "owner_id")
        MODEL_ID_FIELD_NUMBER: _ClassVar[int]
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        SUMMONER_ID_FIELD_NUMBER: _ClassVar[int]
        OWNER_ID_FIELD_NUMBER: _ClassVar[int]
        model_id: int
        level: int
        summoner_id: int
        owner_id: int
        def __init__(self, model_id: _Optional[int] = ..., level: _Optional[int] = ..., summoner_id: _Optional[int] = ..., owner_id: _Optional[int] = ...) -> None: ...
    MONSTER_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_FIELD_NUMBER: _ClassVar[int]
    COMPANION_FIELD_NUMBER: _ClassVar[int]
    monster: EntitySpawnInformation.Monster
    character: EntitySpawnInformation.Character
    companion: EntitySpawnInformation.Companion
    def __init__(self, monster: _Optional[_Union[EntitySpawnInformation.Monster, _Mapping]] = ..., character: _Optional[_Union[EntitySpawnInformation.Character, _Mapping]] = ..., companion: _Optional[_Union[EntitySpawnInformation.Companion, _Mapping]] = ...) -> None: ...
