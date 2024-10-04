import os
from dataclasses import dataclass
from functools import cached_property

import msgspec.json

from resources.gen.gen_datas import (
    ItemsRoot,
    MapPositionsRoot,
    SkillsRoot,
    QuestsRoot,
    QuestObjectivesRoot,
)
from resources.gen.gen_datas import JobsRoot
from src.consts import DOFUS_FOLDER
from src.utils import Singleton


@dataclass(frozen=True)
class DataReader(metaclass=Singleton):
    @cached_property
    def item_by_id(self) -> dict[int, ItemsRoot.Data]:
        with open(
            os.path.join(DOFUS_FOLDER, ItemsRoot.ItemsModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=ItemsRoot.ItemsModel)
        return {
            ref_id.data.id: ref_id.data
            for ref_id in data.references.RefIds
            if ref_id.data.id
        }

    @cached_property
    def job_by_id(self) -> dict[int, JobsRoot.Data]:
        with open(
            os.path.join(DOFUS_FOLDER, JobsRoot.JobsModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=JobsRoot.JobsModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def map_pos_by_map_id(self) -> dict[int, MapPositionsRoot.Data]:
        with open(
            os.path.join(DOFUS_FOLDER, MapPositionsRoot.MapPositionsModel.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(
                file.read(), type=MapPositionsRoot.MapPositionsModel
            )
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def skill_by_id(self) -> dict[int, SkillsRoot.Data]:
        with open(
            os.path.join(DOFUS_FOLDER, SkillsRoot.SkillsModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=SkillsRoot.SkillsModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def quest_by_id(self) -> dict[int, QuestsRoot.Data]:
        with open(
            os.path.join(DOFUS_FOLDER, QuestsRoot.QuestsModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=QuestsRoot.QuestsModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def quest_objective_by_id(self) -> dict[int, QuestObjectivesRoot.Data]:
        with open(
            os.path.join(
                DOFUS_FOLDER, QuestObjectivesRoot.QuestObjectivesModel.FILE_PATH
            ),
            "rb",
        ) as file:
            data = msgspec.json.decode(
                file.read(), type=QuestObjectivesRoot.QuestObjectivesModel
            )
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}


if __name__ == "__main__":
    related_skill_data = next(iter(DataReader().job_by_id.values()))
    print(related_skill_data)
    # temp = related_skill_data
    # print(BinTextParser().i18n_name_by_id[temp])
