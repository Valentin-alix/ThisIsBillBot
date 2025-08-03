from typing import Any

from msgspec import Struct


class MonsterCharacteristic(Struct, frozen=True, kw_only=True):
    lifePoints: int
    strength: int
    wisdom: int
    chance: int
    agility: int
    intelligence: int
    earthResistance: int
    fireResistance: int
    waterResistance: int
    airResistance: int
    neutralResistance: int
    tackleEvade: int
    tackleBlock: int
    bonusEarthDamage: int
    bonusFireDamage: int
    bonusWaterDamage: int
    bonusAirDamage: int
    aPRemoval: int


class MonsterAnimFunListItem(Struct, frozen=True, kw_only=True):
    animId: int
    entityId: int
    animName: str
    animWeight: int


class MonsterCharacRatio(Struct, frozen=True, kw_only=True):
    values: list[float]


class MonsterGrade(Struct, frozen=True, kw_only=True):
    bonusCharacteristics: MonsterCharacteristic
    grade: int
    monsterId: int
    level: int
    lifePoints: int
    actionPoints: int
    movementPoints: int
    vitality: int
    paDodge: int
    pmDodge: int
    wisdom: int
    earthResistance: int
    airResistance: int
    fireResistance: int
    waterResistance: int
    neutralResistance: int
    gradeXp: int
    damageReflect: int
    hiddenLevel: int | None = None
    strength: int
    intelligence: int
    chance: int
    agility: int
    startingSpellId: int
    bonusRange: int


class MonsterGlobalDrop(Struct, frozen=True, kw_only=True):
    objectId: int
    minPercentDrop: float
    maxPercentDrop: float
    receiverCriterion: str
    disableDropModificator: int
    alterationId: int


class MonsterSpecificDropCoefficient(Struct, frozen=True, kw_only=True):
    monsterId: int
    monsterGrade: int
    dropCoefficient: float
    criterions: str


class MonsterDrop(Struct, frozen=True, kw_only=True):
    dropId: int
    monsterId: int
    objectId: int
    percentDropForGrade1: float
    percentDropForGrade2: float
    percentDropForGrade3: float
    percentDropForGrade4: float
    percentDropForGrade5: float
    count: int
    criterions: str
    hasCriterions: int
    hiddenIfInvalidCriterions: int
    disableDropModificator: int
    specificDropCoefficient: list[MonsterSpecificDropCoefficient]


class MonsterSoul(Struct, frozen=True, kw_only=True):
    objectId: int
    criterion: str
    hasCriterion: int


class MonsterItem(Struct, frozen=True, kw_only=True):
    m_flags: int
    id: int
    nameId: int
    gfxId: int
    race: int
    grades: list[MonsterGrade]
    drops: list[MonsterDrop]
    subareas: list[int]
    spells: list[int]
    spellGrades: list[str]
    favoriteSubareaId: int
    isBounty: int
    correspondingMiniBossId: int
    speedAdjust: int
    creatureBoneId: int
    incompatibleChallenges: list[Any]
    incompatibleIdols: list[Any]
    aggressiveZoneSize: int
    aggressiveLevelDiff: int
    aggressiveImmunityCriterion: str
    aggressiveAttackDelay: int
    scaleGradeRef: int
    characRatios: list[MonsterCharacRatio]
    globalDrops: list[MonsterGlobalDrop]
    temporisDrops: list[Any]
    souls: list[MonsterSoul]
    animFunList: list[MonsterAnimFunListItem]
    look: str
    summonCost: int


MonstersRoot = list[MonsterItem]
