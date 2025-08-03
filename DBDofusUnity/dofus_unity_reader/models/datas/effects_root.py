from msgspec import Struct


class EffectsRootItem(Struct, frozen=True, kw_only=True):
    id: int
    descriptionId: int
    iconId: int
    characteristic: int
    category: int
    characteristicOperator: str
    showInTooltip: int
    useDice: int
    forceMinMax: int
    boost: int
    active: int
    oppositeId: int
    theoreticalDescriptionId: str
    theoreticalPattern: int
    showInSet: int
    bonusType: int
    useInFight: int
    effectPriority: int
    effectPowerRate: float
    elementId: int
    isInPercent: int
    hideValueInTooltip: int
    textIconReferenceId: int
    effectTriggerDuration: int
    actionFiltersId: list[int]
    parametersFixed: int


EffectsRoot = list[EffectsRootItem]
