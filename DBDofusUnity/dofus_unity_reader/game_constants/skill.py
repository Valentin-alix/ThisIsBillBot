from enum import IntEnum


class SkillEnum(IntEnum):
    PHOENIX = 211
    EXIT = 184
    POINT_OUT_EXIT = 339
    SCIER = 101
    PREPARER_POTION = 23
    POLIR_PIERRE = 48
    FONDRE = 32
    MOUDRE = 47
    CUIRE = 27
    PREPARER_POISSON = 135
    PREPARER_VIANDE = 134


# Map IDs (workshop) par skill ID
MAP_IDS_BY_SKILL: dict[int, set[int]] = {
    SkillEnum.SCIER: {217063430, 192940034},  # bucheron
    SkillEnum.PREPARER_POTION: {217057284, 192937988},  # alchimiste
    SkillEnum.POLIR_PIERRE: {217061380, 192939010},  # mineur
    SkillEnum.FONDRE: {217060356, 192939010},  # mineur
    SkillEnum.MOUDRE: {217061382, 192939008},  # paysan
    SkillEnum.CUIRE: {217061382, 192939008},  # paysan
    SkillEnum.PREPARER_POISSON: {217062406, 192937984},  # pecheur
    SkillEnum.PREPARER_VIANDE: {192937994},  # chasseur
}
