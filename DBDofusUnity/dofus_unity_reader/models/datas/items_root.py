from __future__ import annotations

from typing import Any

from msgspec import Struct, field

from DBDofusUnity.dofus_unity_reader.models.datas.zone_descr import ZoneDescr


class PossibleEffect(Struct, frozen=True, kw_only=True):
    rid: int


class ResourcesBySubareaItem(Struct, frozen=True, kw_only=True):
    values: list[int]


class ItemsRootItemStrict(Struct, frozen=True, kw_only=True):
    m_flags: int
    id: int | None = None
    typeId: int | None = None
    nameId: int | None = None
    descriptionId: int | None = None
    iconId: int | None = None
    level: int | None = None
    realWeight: int | None = None
    useAnimationId: int | None = None
    price: float | None = None
    itemSetId: int | None = None
    criterions: str | None = None
    criterionsTarget: str | None = None
    appearanceId: int | None = None
    isColorable: int | None = None
    recipeSlots: int | None = None
    recipeIds: list[int] | None = None
    dropMonsterIds: list[int] | None = None
    dropTemporisMonsterIds: list[Any] | None = None
    possibleEffects: list[PossibleEffect] | None = None
    evolutiveEffectIds: list[int] | None = None
    favoriteSubAreas: list[Any] | None = None
    favoriteSubAreasBonus: int | None = None
    craftXpRatio: int | None = None
    craftVisibleCriterion: str | None = None
    craftConditionalCriterion: str | None = None
    craftFeasibleCriterion: str | None = None
    visibilityCriterion: str | None = None
    recyclingNuggets: float | None = None
    favoriteRecyclingSubareas: list[int] | None = None
    resourcesBySubarea: list[ResourcesBySubareaItem] | None = None
    importantNoticeId: str | None = None
    changeVersion: str | None = None
    tooltipExpirationDate: float | str | None = None
    criticalFailureProbability: int | None = None
    criticalHitBonus: int | None = None
    minRange: int | None = None
    criticalHitProbability: int | None = None
    range: int | None = None
    castInLine: int | None = None
    apCost: int | None = None
    castInDiagonal: int | None = None
    castTestLos: int | None = None
    maxCastPerTurn: int | None = None
    effectUid: int | None = None
    baseEffectId: int | None = None
    effectId: int | None = field(default=None, name="actionId")
    order: int | None = None
    targetId: int | None = None
    targetMask: str | None = None
    duration: int | None = None
    random: float | None = None
    group: int | None = None
    modificator: int | None = None
    dispellable: int | None = None
    delay: int | None = None
    triggers: str | None = None
    effectElement: int | None = None
    spellId: int | None = None
    effectTriggerDuration: int | None = None
    zoneDescr: ZoneDescr | None = None
    value: int | None = None
    diceNum: int | None = None
    diceSide: int | None = None
    displayZero: int | None = None

    def __hash__(self):
        return self.id.__hash__()  # ty:ignore[missing-argument]


class ItemsRootItemEffect(Struct, frozen=True, kw_only=True):
    id: None = None
    effectId: int = field(name="actionId")
    diceNum: int
    diceSide: int


class ItemsRootItem(ItemsRootItemStrict):
    id: int
    typeId: int
    nameId: int
    possibleEffects: list[PossibleEffect] | None = None


ItemsRoot = list[ItemsRootItemStrict]
