from msgspec import Struct


class ZoneDescr(Struct, frozen=True, kw_only=True):
    cellIds: list[int]
    shape: int
    param1: int
    param2: int
    damageDecreaseStepPercent: int
    maxDamageDecreaseApplyCount: int
    isStopAtTarget: int
    forcedDirection: int
    includeCarried: int
    onlyAffectIfInSightLine: int
