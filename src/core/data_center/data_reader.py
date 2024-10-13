import os
import zlib
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from typing import Any

import icecream
import msgspec.json

from D3Database.consts import D3_DATA
from models.datas.areas_root import AreasRoot, AreasRootItem
from models.datas.characteristic_category_root import CharacteristicCategoriesRoot
from models.datas.characteristic_root import (
    CharacteristicsRoot,
    CharacteristicsRootItem,
)
from models.datas.effects_root import EffectsRootItem, EffectsRoot
from models.datas.item_type_root import ItemsTypeRoot
from models.datas.items_root import ItemsRoot, ItemsRootItem
from models.datas.jobs_root import JobsRoot, JobsRootItem
from models.datas.map_positions_root import MapPositionsRoot, MapPositionsRootItem
from models.datas.monsters_root import MonsterItem, MonstersRoot
from models.datas.quest_objectives_root import (
    QuestObjectivesRoot,
    QuestObjectivesRootItem,
)
from models.datas.quests_root import QuestsRoot, QuestsRootItem
from models.datas.recipe_root import RecipeItem, RecipeRoot
from models.datas.skills_root import SkillsRoot, SkillsRootItem
from models.datas.spell_levels_root import SpellLevelsRoot, SpellLevelsRootItem
from models.datas.spell_variants_root import SpellVariantsRoot, SpellVariantsRootItem
from models.datas.spells_root import SpellsRoot, SpellsRootItem
from models.datas.sub_areas_root import SubAreasRoot, SubAreasRootItem
from models.datas.waypoints_root import WaypointsRoot, WaypointsRootItem
from src.core.data_center.i18n import I18N
from src.interfaces.enums.job_enum import HARVESTER_JOB_IDS
from src.interfaces.metaclasses.singleton import Singleton

FILEPATH_BY_MODEL: dict[Any, str] = {
    AreasRoot: "AreasRoot.json",
    ItemsRoot: "ItemsRoot.json",
    ItemsTypeRoot: "ItemTypesRoot.json",
    RecipeRoot: "RecipesRoot.json",
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
    MonstersRoot: "MonstersRoot.json",
}


@dataclass(frozen=True)
class DataReader(metaclass=Singleton):
    @cached_property
    def item_by_id(self) -> dict[int, ItemsRootItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[ItemsRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=ItemsRoot)
        return {item.id: item for item in data if item.id is not None}

    @cached_property
    def recipes(self) -> list[RecipeItem]:
        with open(os.path.join(D3_DATA, FILEPATH_BY_MODEL[RecipeRoot]), "rb") as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=RecipeRoot)
        return data

    @cached_property
    def recipe_by_result_id(self) -> dict[int, RecipeItem]:
        return {recipe.resultId: recipe for recipe in self.recipes}

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
    def sub_areas_by_area_id(self) -> dict[int, set[int]]:
        sub_area_ids_by_area_id_dict: dict[int, set[int]] = defaultdict(set)
        for sub_area in DataReader().sub_area_by_id.values():
            sub_area_ids_by_area_id_dict[sub_area.areaId].add(sub_area.id)
        return sub_area_ids_by_area_id_dict

    @cached_property
    def monsters_by_id(self) -> dict[int, MonsterItem]:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[MonstersRoot]),
            "rb",
        ) as file:
            data = msgspec.json.decode(zlib.decompress(file.read()), type=MonstersRoot)
        return {monster.id: monster for monster in data}

    @cached_property
    def monsters_by_race(self) -> dict[int, list[MonsterItem]]:
        monsters_by_race_dict: defaultdict[int, list[MonsterItem]] = defaultdict(list)
        for monster in DataReader().monsters_by_id.values():
            monsters_by_race_dict[monster.race].append(monster)
        return monsters_by_race_dict

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
    def gathered_item_ids(self) -> set[int]:
        return {
            skill.gatheredRessourceItem
            for skill in self.skill_by_id.values()
            if skill.parentJobId in HARVESTER_JOB_IDS
            and skill.gatheredRessourceItem not in [-1, 0]
        }

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
    def spell_variants(self) -> SpellVariantsRoot:
        with open(
            os.path.join(D3_DATA, FILEPATH_BY_MODEL[SpellVariantsRoot]), "rb"
        ) as file:
            return msgspec.json.decode(
                zlib.decompress(file.read()), type=SpellVariantsRoot
            )

    @cached_property
    def spell_variant_by_breed_id(self) -> dict[int, list[SpellVariantsRootItem]]:
        _spell_variant_by_breed_id: dict[int, list[SpellVariantsRootItem]] = (
            defaultdict(list)
        )
        for spell_variant in self.spell_variants:
            _spell_variant_by_breed_id[spell_variant.breedId].append(spell_variant)
        return _spell_variant_by_breed_id

    @cached_property
    def spell_opposite_variant_by_spell_id(self) -> dict[int, int]:
        data = self.spell_variants
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
    spell_id = 12724
    spell = DataReader().spell_by_id[spell_id]
    spell_lvl = DataReader().spell_lvl_by_spell_id[spell_id][0]
    for effect in spell_lvl.effects:
        data_effect = DataReader().effect_by_id[effect.effectId]
        icecream.ic(effect)
        print(I18N.name_by_id[data_effect.descriptionId])
        # icecream.ic(char)
    print(I18N.name_by_id[spell.nameId])
