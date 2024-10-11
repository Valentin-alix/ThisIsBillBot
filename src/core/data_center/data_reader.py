import os
import zlib
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from typing import Any

import msgspec.json
from icecream import icecream

from D3Database.consts import D3_DATA
from models.datas.areas_root import AreasRoot, AreasRootItem
from models.datas.characteristic_category_root import CharacteristicCategoriesRoot
from models.datas.characteristic_root import (
    CharacteristicsRoot,
    CharacteristicsRootItem,
)
from models.datas.effects_root import EffectsRootItem, EffectsRoot
from models.datas.items_root import ItemsRoot, ItemsRootItem
from models.datas.jobs_root import JobsRoot, JobsRootItem
from models.datas.map_positions_root import MapPositionsRoot, MapPositionsRootItem
from models.datas.quest_objectives_root import (
    QuestObjectivesRoot,
    QuestObjectivesRootItem,
)
from models.datas.quests_root import QuestsRoot, QuestsRootItem
from models.datas.skills_root import SkillsRoot, SkillsRootItem
from models.datas.spell_levels_root import SpellLevelsRoot, SpellLevelsRootItem
from models.datas.spell_variants_root import SpellVariantsRoot
from models.datas.spells_root import SpellsRoot, SpellsRootItem
from models.datas.sub_areas_root import SubAreasRoot, SubAreasRootItem
from models.datas.waypoints_root import WaypointsRoot, WaypointsRootItem
from src.core.data_center.i18n import I18N
from src.interfaces.metaclasses.singleton import Singleton

FILEPATH_BY_MODEL: dict[Any, str] = {
    AreasRoot: "AreasRoot.json",
    ItemsRoot: "ItemsRoot.json",
    JobsRoot: "JobsRoot.json",
    MapPositionsRoot: "MapPositionsRoot.json",
    QuestObjectivesRoot: "QuestObjectivesRoot.json",
    QuestsRoot: "QuestsRoot.json",
    SkillsRoot: "SkillsRoot.json",
    SpellLevelsRoot: "SpellLevelsRoot.json",
    SpellsRoot: "SpellsRoot.json",
    SpellVariantsRoot: "SpellVariantsRoot.json",
    SubAreasRoot: "SubAreasRoot.json",
    WaypointsRoot: "WaypointsRoot.json",
    EffectsRoot: "EffectsRoot.json",
    CharacteristicsRoot: "CharacteristicsRoot.json",
    CharacteristicCategoriesRoot: "CharacteristicCategoriesRoot.json",
}


@dataclass(frozen=True)
class DataReader(metaclass=Singleton):
    @cached_property
    def item_by_id(self) -> dict[int, ItemsRootItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[ItemsRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=ItemsRoot)
        return {item.id: item for item in data if item.id is not None}

    @cached_property
    def job_by_id(self) -> dict[int, JobsRootItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[JobsRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=JobsRoot)
        return {job.id: job for job in data}

    @cached_property
    def map_pos_by_map_id(self) -> dict[int, MapPositionsRootItem]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[MapPositionsRoot]),
            "rb",
        ) as file:
            data = msgspec.json.decode(
                zlib.decompress(file.read()), type=MapPositionsRoot
            )
        return {map_pos.id: map_pos for map_pos in data}

    @cached_property
    def map_pos_by_coord(self) -> dict[tuple[int, int], list[MapPositionsRootItem]]:
        map_pos_by_coord_dict: dict[tuple[int, int], list[MapPositionsRootItem]] = (
            defaultdict(list)
        )
        for map_pos in self.map_pos_by_map_id.values():
            map_pos_by_coord_dict[(map_pos.posX, map_pos.posY)].append(map_pos)
        return map_pos_by_coord_dict

    @cached_property
    def sub_area_by_id(self) -> dict[int, SubAreasRootItem]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[SubAreasRoot]),
            "rb",
        ) as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=SubAreasRoot)
        return {sub_area.id: sub_area for sub_area in data}

    @cached_property
    def area_by_id(self) -> dict[int, AreasRootItem]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[AreasRoot]),
            "rb",
        ) as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=AreasRoot)
        return {area.id: area for area in data}

    @cached_property
    def map_ids_by_area_id(self) -> dict[int, set[int]]:
        _map_ids: dict[int, set[int]] = defaultdict(set)
        for sub_area in DataReader().sub_area_by_id.values():
            _map_ids[sub_area.areaId] |= set(
                DataReader().sub_area_by_id[sub_area.id].mapIds
            )
        return _map_ids

    @cached_property
    def waypoint_by_id(self) -> dict[int, WaypointsRootItem]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[WaypointsRoot]),
            "rb",
        ) as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=WaypointsRoot)
        return {waypoint.id: waypoint for waypoint in data}

    @cached_property
    def skill_by_id(self) -> dict[int, SkillsRootItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[SkillsRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=SkillsRoot)
        return {skill.id: skill for skill in data}

    @cached_property
    def quest_by_id(self) -> dict[int, QuestsRootItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[QuestsRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=QuestsRoot)
        return {quest.id: quest for quest in data}

    @cached_property
    def quest_objective_by_id(self) -> dict[int, QuestObjectivesRootItem]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[QuestObjectivesRoot]),
            "rb",
        ) as file:
            data = msgspec.json.decode(
                zlib.decompress(file.read()), type=QuestObjectivesRoot
            )
        return {quest_obj.id: quest_obj for quest_obj in data}

    @cached_property
    def spell_by_id(self) -> dict[int, SpellsRootItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[SpellsRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=SpellsRoot)
        return {spell.id: spell for spell in data}

    @cached_property
    def effect_by_id(self) -> dict[int, EffectsRootItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[EffectsRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=EffectsRoot)
        return {effect.id: effect for effect in data}

    @cached_property
    def characteristic_by_id(self) -> dict[int, CharacteristicsRootItem]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[CharacteristicsRoot]), "rb"
        ) as file:
            data = msgspec.json.decode(
                zlib.decompress(file.read()), type=CharacteristicsRoot
            )
        return {characteristic.id: characteristic for characteristic in data}

    @cached_property
    def spell_opposite_variant_by_spell_id(self) -> dict[int, int]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[SpellVariantsRoot]), "rb"
        ) as file:
            data = msgspec.json.decode(
                zlib.decompress(file.read()), type=SpellVariantsRoot
            )

        spell_opposite_variant: dict[int, int] = {}
        for spell_variant in data:
            first_spell_id = spell_variant.spellIds[0]
            second_spell_id = spell_variant.spellIds[1]
            spell_opposite_variant[first_spell_id] = second_spell_id
            spell_opposite_variant[second_spell_id] = first_spell_id

        return spell_opposite_variant

    @cached_property
    def spell_lvl_by_spell_id(self) -> dict[int, list[SpellLevelsRootItem]]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[SpellLevelsRoot]),
            "rb",
        ) as file:
            data = msgspec.json.decode(
                zlib.decompress(file.read()), type=SpellLevelsRoot
            )

        spell_levels_by_spell_id: dict[int, list[SpellLevelsRootItem]] = defaultdict(
            list
        )
        for spell_lvl in data:
            spell_levels_by_spell_id[spell_lvl.spellId].append(spell_lvl)
            spell_levels_by_spell_id[spell_lvl.spellId].sort(
                key=lambda spell_lvl: spell_lvl.minPlayerLevel
            )

        return spell_levels_by_spell_id


if __name__ == "__main__":
    spell_id = 12728

    DataReader().item_by_id

    spell = DataReader().spell_by_id[spell_id]
    spell_lvl = DataReader().spell_lvl_by_spell_id[spell_id][0]
    for effect in spell_lvl.effects:
        data_effect = DataReader().effect_by_id[effect.effectId]
        # char = DataReader().characteristic_by_id[data_effect.characteristic]
        icecream.ic(effect)
        icecream.ic(data_effect)
        print(I18N.name_by_id[data_effect.descriptionId])
        # icecream.ic(char)
    print(I18N.name_by_id[spell.nameId])
