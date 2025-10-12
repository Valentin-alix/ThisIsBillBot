from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    CharacterCharacteristic,
    CharacterCharacteristicValue,
)
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.game_constants.job import JobEnum
from DBDofusUnity.dofus_unity_reader.models.datas.effects_root import EffectsRootItem
from DBDofusUnity.dofus_unity_reader.models.datas.item_type_root import ItemTypeData
from DBDofusUnity.dofus_unity_reader.models.datas.items_root import ItemsRootItemStrict
from DBDofusUnity.dofus_unity_reader.models.datas.recipe_root import RecipeItem
from DBDofusUnity.dofus_unity_reader.models.datas.skills_root import SkillsRootItem
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)
from DBDofusUnity.dofus_unity_reader.models.datas.zone_descr import ZoneDescr


def make_skill_data(
    *,
    skill_id: int = 1,
    level_min: int = 1,
    parent_job_id: int = JobEnum.PEASANT,
    gathered_resource_item: int = 100,
) -> SkillsRootItem:
    return SkillsRootItem(
        id=skill_id,
        nameId=0,
        parentJobId=parent_job_id,
        isForgemagus=0,
        modifiableItemTypeIds=[],
        gatheredRessourceItem=gathered_resource_item,
        craftableItemIds=[],
        interactiveId=0,
        range=0,
        useRangeInClient=0,
        useAnimation="",
        cursor=0,
        elementActionId=0,
        availableInHouse=0,
        clientDisplay=0,
        levelMin=level_min,
        allowMarking=0,
    )


def make_item_data(
    *,
    gid: int = 1,
    type_id: int | None = 1,
    level: int | None = 1,
    craft_conditional_criterion: str | None = None,
) -> ItemsRootItemStrict:
    return ItemsRootItemStrict(
        m_flags=0,
        id=gid,
        typeId=type_id,
        nameId=0,
        level=level,
        craftConditionalCriterion=craft_conditional_criterion,
    )


def make_item_type_data(
    *,
    type_id: int = 1,
    category_id: int = 0,
) -> ItemTypeData:
    return ItemTypeData(
        id=type_id,
        nameId=0,
        superTypeId=0,
        categoryId=category_id,
        isInEncyclopedia=0,
        craftXpRatio=0,
        evolutiveTypeId=0,
        rawZone="",
    )


def make_characteristics(
    values: dict[int, int],
) -> dict[int, CharacterCharacteristic]:
    """Build a characteristic_by_id map from {characteristic_id: total} values."""
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


def make_effect_data(characteristic_operator: str = "") -> EffectsRootItem:
    return EffectsRootItem(
        id=1,
        descriptionId=0,
        iconId=0,
        characteristic=0,
        category=0,
        characteristicOperator=characteristic_operator,
        showInTooltip=0,
        useDice=0,
        forceMinMax=0,
        boost=0,
        active=0,
        oppositeId=0,
        theoreticalDescriptionId="",
        theoreticalPattern=0,
        showInSet=0,
        bonusType=0,
        useInFight=0,
        effectPriority=0,
        effectPowerRate=0.0,
        elementId=0,
        isInPercent=0,
        hideValueInTooltip=0,
        textIconReferenceId=0,
        effectTriggerDuration=0,
        actionFiltersId=[],
        parametersFixed=0,
    )


def make_recipe(
    *,
    result_id: int = 100,
    result_level: int = 10,
    ingredient_ids: list[int] | None = None,
    quantities: list[int] | None = None,
    job_id: int = JobEnum.ALCHEMIST,
    skill_id: int = 23,
) -> RecipeItem:
    return RecipeItem(
        resultId=result_id,
        resultNameId=str(result_id),
        resultTypeId=0,
        resultLevel=result_level,
        ingredientIds=ingredient_ids or [50, 51],
        quantities=quantities or [2, 3],
        jobId=job_id,
        skillId=skill_id,
    )
