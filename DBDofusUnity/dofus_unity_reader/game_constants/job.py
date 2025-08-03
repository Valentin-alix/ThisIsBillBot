from enum import IntEnum


class JobEnum(IntEnum):
    BASE = 1
    WOODCUTTER = 2
    MINER = 24
    ALCHEMIST = 26
    PEASANT = 28
    FISHERMAN = 36
    CHASSEUR = 41


HARVESTER_JOB_IDS: set[JobEnum] = {
    JobEnum.MINER,
    JobEnum.WOODCUTTER,
    JobEnum.PEASANT,
    JobEnum.FISHERMAN,
    JobEnum.ALCHEMIST,
    JobEnum.BASE,
}
