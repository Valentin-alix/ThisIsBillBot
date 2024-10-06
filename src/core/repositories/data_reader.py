import os
from collections import defaultdict
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
    SpellLevelsRoot,
    WaypointsRoot,
)
from src.interfaces.metaclasses.singleton import Singleton


@dataclass(frozen=True)
class DataReader(metaclass=Singleton):
    @cached_property
    def item_by_id(self) -> dict[int, ItemsRoot.Data]:
        with open(os.path.join(DOFUS_PATH, ItemsRoot.Model.FILE_PATH), "rb") as file:
            data = msgspec.json.decode(file.read(), type=ItemsRoot.Model)
        return {
            ref_id.data.id: ref_id.data
            for ref_id in data.references.RefIds
            if ref_id.data.id
        }

    @cached_property
    def job_by_id(self) -> dict[int, JobsRoot.Data]:
        with open(os.path.join(DOFUS_PATH, JobsRoot.Model.FILE_PATH), "rb") as file:
            data = msgspec.json.decode(file.read(), type=JobsRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def map_pos_by_map_id(self) -> dict[int, MapPositionsRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, MapPositionsRoot.Model.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(file.read(), type=MapPositionsRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def sub_area_by_id(self) -> dict[int, SubAreasRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, SubAreasRoot.Model.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(file.read(), type=SubAreasRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def waypoint_by_id(self) -> dict[int, WaypointsRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, WaypointsRoot.Model.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(file.read(), type=WaypointsRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def skill_by_id(self) -> dict[int, SkillsRoot.Data]:
        with open(os.path.join(DOFUS_PATH, SkillsRoot.Model.FILE_PATH), "rb") as file:
            data = msgspec.json.decode(file.read(), type=SkillsRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def skill_names_by_id(self) -> dict[int, SkillNamesRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, SkillNamesRoot.Model.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=SkillNamesRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def quest_by_id(self) -> dict[int, QuestsRoot.Data]:
        with open(os.path.join(DOFUS_PATH, QuestsRoot.Model.FILE_PATH), "rb") as file:
            data = msgspec.json.decode(file.read(), type=QuestsRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def quest_objective_by_id(self) -> dict[int, QuestObjectivesRoot.Data]:
        with open(
            os.path.join(DOFUS_PATH, QuestObjectivesRoot.Model.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(file.read(), type=QuestObjectivesRoot.Model)
        return {ref_id.data.id: ref_id.data for ref_id in data.references.RefIds}

    @cached_property
    def spell_lvl_by_spell_id(self) -> dict[int, list[SpellLevelsRoot.Data]]:
        with open(
            os.path.join(DOFUS_PATH, SpellLevelsRoot.Model.FILE_PATH),
            "rb",
        ) as file:
            data = msgspec.json.decode(file.read(), type=SpellLevelsRoot.Model)

        spell_levels_by_spell_id: dict[int, list[SpellLevelsRoot.Data]] = defaultdict(
            list
        )
        for ref_id in data.references.RefIds:
            spell_levels_by_spell_id[ref_id.data.spellId].append(ref_id.data)
            spell_levels_by_spell_id[ref_id.data.spellId].sort(
                key=lambda spell_lvl: spell_lvl.minPlayerLevel
            )

        return spell_levels_by_spell_id


if __name__ == "__main__":
    related_skill_data = DataReader().map_pos_by_map_id[153879813]
    print(related_skill_data)
    # temp = related_skill_data
    # print(BinTextParser().i18n_name_by_id[temp])
