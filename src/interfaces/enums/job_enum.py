from enum import IntEnum

from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N


class JobEnum(IntEnum):
    BASE = 1
    WOODCUTTER = 2
    MINER = 24
    ALCHEMIST = 26
    PEASANT = 28
    FISHERMAN = 36


if __name__ == "__main__":
    for job in DataReader().job_by_id.values():
        name = I18N.name_by_id[job.nameId]
        print(name)
