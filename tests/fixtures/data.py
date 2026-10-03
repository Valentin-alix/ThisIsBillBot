from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    CharacterCharacteristic,
    CharacterCharacteristicValue,
)
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)
from DBDofusUnity.dofus_unity_reader.models.datas.zone_descr import ZoneDescr


def make_characteristics(
    values: dict[int, int],
) -> dict[int, CharacterCharacteristic]:
    return {
        characteristic_id: CharacterCharacteristic(
            characteristic_id=characteristic_id,
            value=CharacterCharacteristicValue(total=value),
        )
        for characteristic_id, value in values.items()
    }


def make_zone_descr() -> ZoneDescr:
    return ZoneDescr(
        cellIds=[],
        shape=0,
        param1=0,
        param2=0,
        damageDecreaseStepPercent=0,
        maxDamageDecreaseApplyCount=0,
        isStopAtTarget=0,
        forcedDirection=0,
        includeCarried=0,
        onlyAffectIfInSightLine=0,
    )


def make_spell_effect(effect_id: int, effect_element: EffectElement) -> Effect:
    return Effect(
        m_flags=0,
        effectUid=effect_id,
        baseEffectId=effect_id,
        effectId=effect_id,
        order=0,
        targetId=0,
        targetMask="",
        duration=0,
        random=0,
        group=0,
        modificator=0,
        dispellable=0,
        delay=0,
        triggers="",
        effectElement=effect_element,
        spellId=1,
        effectTriggerDuration=0,
        zoneDescr=make_zone_descr(),
        value=0,
        diceNum=0,
        diceSide=0,
        displayZero=0,
    )


def make_spell_level(
    *,
    range_value: int = 0,
    min_range: int = 0,
    flags: int = 0,
    states_criterion: str = "",
    global_cooldown: int = 0,
    initial_cooldown: int = 0,
    effects: list[Effect] | None = None,
) -> SpellLevelsRootItem:
    return SpellLevelsRootItem(
        m_flags=flags,
        id=1,
        spellId=1,
        grade=1,
        spellBreed=0,
        apCost=3,
        minRange=min_range,
        range=range_value,
        criticalHitProbability=0,
        maxStack=0,
        maxCastPerTurn=0,
        maxCastPerTarget=0,
        minCastInterval=0,
        initialCooldown=initial_cooldown,
        globalCooldown=global_cooldown,
        minPlayerLevel=1,
        statesCriterion=states_criterion,
        effects=effects or [],
        criticalEffect=[],
        previewZones=[],
    )
