from enums.jobs_enum import JobEnum

WEIGHT_BY_JOB: dict[JobEnum, float] = {
    JobEnum.MINER: 10,
    JobEnum.WOODCUTTER: 10,
    JobEnum.ALCHEMIST: 10,
    JobEnum.PEASANT: 1,
    JobEnum.FISHERMAN: 5,
    JobEnum.BASE: 1,
}
