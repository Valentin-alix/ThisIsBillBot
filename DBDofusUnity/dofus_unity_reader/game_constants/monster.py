from enum import IntEnum


class MonsterGidEnum(IntEnum):
    POUTCH = 494
    PRESPIC = 103


class MonsterRaceEnum(IntEnum):
    PROTECTEUR_ALCHIMISTE = 66
    PROTECTEUR_PECHEUR = 65
    PROTECTEUR_BUCHERON = 64
    PROTECTEUR_MINEUR = 63
    PROTECTEUR_PAYSAN = 62


PROTECTOR_RACES: list[MonsterRaceEnum] = list(MonsterRaceEnum)
