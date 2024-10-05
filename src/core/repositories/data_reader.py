import os
from dataclasses import dataclass
from functools import cached_property

import msgspec.json

from db_dofus_unity.consts import DOFUS_PATH
from db_dofus_unity.gen.gen_datas import (
    ItemsRoot,
    JobsRoot,
    MapPositionsRoot,
    SkillsRoot,
    QuestsRoot,
    QuestObjectivesRoot,
    SubAreasRoot,
    SkillNamesRoot,
)
from src.interfaces.metaclasses.singleton import Singleton


@dataclass(frozen=True)
class DataReader(metaclass=Singleton):

    def load_cached_properties(self):
        for attr in dir(self):
            if isinstance(getattr(self.__class__, attr, None), cached_property):
                getattr(self, attr)

    @cached_property
    def item_by_id(self) -> dict[int, ItemsRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, ItemsRoot.ItemsModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=ItemsRoot.ItemsModel)
        return {
            ref_id.data.id: ref_id.data
            for ref_id in data.references.RefIds
            if ref_id.data.id
        }

    @cached_property
    def job_by_id(self) -> dict[int, JobsRoot.Data]:
        with open(os.path.join(DOFUS_PATH, JobsRoot.JobsModel.FILE_PATH), "rb") as file:
            data = msgspec.json.decode(file.read(), type=JobsRoot.JobsModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def map_pos_by_map_id(self) -> dict[int, MapPositionsRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, MapPositionsRoot.MapPositionsModel.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(
                file.read(), type=MapPositionsRoot.MapPositionsModel
            )
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def sub_area_by_id(self) -> dict[int, SubAreasRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, SubAreasRoot.SubAreasModel.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(file.read(), type=SubAreasRoot.SubAreasModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def skill_by_id(self) -> dict[int, SkillsRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, SkillsRoot.SkillsModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=SkillsRoot.SkillsModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def skill_names_by_id(self) -> dict[int, SkillNamesRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, SkillNamesRoot.SkillNamesModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=SkillNamesRoot.SkillNamesModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def quest_by_id(self) -> dict[int, QuestsRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, QuestsRoot.QuestsModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=QuestsRoot.QuestsModel)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def quest_objective_by_id(self) -> dict[int, QuestObjectivesRoot.Data]:
        with open(
            os.path.join(
                DOFUS_PATH, QuestObjectivesRoot.QuestObjectivesModel.FILE_PATH
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
