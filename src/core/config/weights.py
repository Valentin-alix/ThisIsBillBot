from enums.jobs_enum import JobEnum

WEIGHT_BY_JOB: dict[JobEnum, float] = {
    JobEnum.MINER: 5,
    JobEnum.WOODCUTTER: 5,
    JobEnum.ALCHEMIST: 5,
    JobEnum.FISHERMAN: 5,
    JobEnum.PEASANT: 2.5,
    JobEnum.BASE: 1,
}
