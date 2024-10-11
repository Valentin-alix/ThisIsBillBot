from src.interfaces.enums.job_enum import JobEnum

HARVESTER_JOB_IDS: set[JobEnum] = {
    JobEnum.MINER,
    JobEnum.WOODCUTTER,
    JobEnum.PEASANT,
    JobEnum.FISHERMAN,
    JobEnum.ALCHEMIST,
    JobEnum.BASE,
}
