from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar, TypeVar

import msgspec
import msgspec.json
from base_python.cache import cache
from base_python.singleton import Singleton
from consts import DATA_BUNDLES_ROOT, MAP_BUNDLES_ROOT
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from dofus_unity_reader.game_constants.item import CategoryItemEnum
from dofus_unity_reader.game_constants.job import HARVESTER_JOB_IDS
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD
from dofus_unity_reader.models.datas.areas_root import AreasRoot, AreasRootItem
from dofus_unity_reader.models.datas.breedsroot import Breedsroot, BreedsrootItem
from dofus_unity_reader.models.datas.characteristic_category_root import (
    CharacteristicCategoriesRoot,
)
from dofus_unity_reader.models.datas.characteristic_root import (
    CharacteristicsRoot,
    CharacteristicsRootItem,
)
from dofus_unity_reader.models.datas.dungeons_root import DungeonsRoot, DungeonsRootItem
from dofus_unity_reader.models.datas.effects_root import EffectsRoot, EffectsRootItem
from dofus_unity_reader.models.datas.item_type_root import ItemsTypeRoot, ItemTypeData
from dofus_unity_reader.models.datas.items_root import (
    ItemsRoot,
    ItemsRootItem,
    ItemsRootItemEffect,
    ItemsRootItemStrict,
)
from dofus_unity_reader.models.datas.jobs_root import JobsRoot, JobsRootItem
from dofus_unity_reader.models.datas.map_positions_root import (
    MapInformationRootItem,
    MapInformationsRoot,
)
from dofus_unity_reader.models.datas.monsters_root import MonsterItem, MonstersRoot
from dofus_unity_reader.models.datas.npc_actions_root import NpcActionsRoot, NpcActionsRootItem
from dofus_unity_reader.models.datas.npc_messages_root import (
    NpcMessagesRoot,
    NpcMessagesRootItem,
)
from dofus_unity_reader.models.datas.npcs_root import NpcsRoot, NpcsRootItem
from dofus_unity_reader.models.datas.quest_objectives_root import (
    QuestObjectivesRoot,
    QuestObjectivesRootItem,
)
from dofus_unity_reader.models.datas.quests_root import QuestsRoot, QuestsRootItem
from dofus_unity_reader.models.datas.queststepsroot import (
    Queststepsroot,
    QueststepsrootItem,
)
from dofus_unity_reader.models.datas.recipe_root import RecipeItem, RecipeRoot
from dofus_unity_reader.models.datas.skills_root import SkillsRoot, SkillsRootItem
from dofus_unity_reader.models.datas.spell_levels_root import (
    SpellLevelsRoot,
    SpellLevelsRootItem,
)
from dofus_unity_reader.models.datas.spell_variants_root import (
    SpellVariantsRoot,
    SpellVariantsRootItem,
)
from dofus_unity_reader.models.datas.spells_root import SpellsRoot, SpellsRootItem
from dofus_unity_reader.models.datas.sub_areas_root import SubAreasRoot, SubAreasRootItem
from dofus_unity_reader.models.datas.waypoints_root import WaypointsRoot, WaypointsRootItem

FILEPATH_BY_MODEL: dict[Any, str] = {
    AreasRoot: "AreasDataRoot.json",
    ItemsRoot: "ItemsDataRoot.json",
    ItemsTypeRoot: "ItemTypesDataRoot.json",
    RecipeRoot: "RecipesDataRoot.json",
    JobsRoot: "JobsDataRoot.json",
    MapInformationsRoot: "MapsInformationDataRoot.json",
    QuestObjectivesRoot: "QuestObjectivesDataRoot.json",
    QuestsRoot: "QuestsDataRoot.json",
    Queststepsroot: "QuestStepsDataRoot.json",
    SkillsRoot: "SkillsDataRoot.json",
    SpellLevelsRoot: "SpellLevelsDataRoot.json",
    SpellsRoot: "SpellsDataRoot.json",
    SpellVariantsRoot: "SpellVariantsDataRoot.json",
    SubAreasRoot: "SubAreasDataRoot.json",
    WaypointsRoot: "WaypointsDataRoot.json",
    EffectsRoot: "EffectsDataRoot.json",
    CharacteristicsRoot: "CharacteristicsDataRoot.json",
    CharacteristicCategoriesRoot: "CharacteristicCategoriesDataRoot.json",
    MonstersRoot: "MonstersDataRoot.json",
    DungeonsRoot: "DungeonsDataRoot.json",
    NpcActionsRoot: "NpcActionsDataRoot.json",
    NpcMessagesRoot: "NpcMessagesDataRoot.json",
    NpcsRoot: "NpcsDataRoot.json",
    Breedsroot: "BreedsDataRoot.json",
}

_MIN_DUNGEON_MAP_COUNT = 2


def _data_file_path(model: type[msgspec.Struct] | type[Sequence[msgspec.Struct]]) -> Path:
    return DATA_BUNDLES_ROOT / FILEPATH_BY_MODEL[model]


def _read_json_bytes(bundle_path: Path) -> bytes:
    with bundle_path.open("rb") as file:
        return file.read()


_T = TypeVar("_T")


def _load_model(model: type[msgspec.Struct] | type[Sequence[msgspec.Struct]], type_: type[_T]) -> _T:
    return msgspec.json.decode(_read_json_bytes(_data_file_path(model)), type=type_)


def _coerce_item_root_item(item: ItemsRootItemStrict) -> ItemsRootItem | None:
    if item.id is None or item.typeId is None or item.nameId is None:
        return None
    return msgspec.convert(msgspec.to_builtins(item), type=ItemsRootItem)


@dataclass(frozen=True)
class DataReader(metaclass=Singleton):
    POSSIBLE_COORD_X: ClassVar[set[int]] = {x for x, _ in MAP_POINT_BY_COORD}
    POSSIBLE_COORD_Y: ClassVar[set[int]] = {y for _, y in MAP_POINT_BY_COORD}
    POSSIBLE_ELEMENT_STATES: ClassVar[set[int]] = {0, 1, 2}
    SPELL_NUMEROS: ClassVar[set[int]] = {0, 1, 2}

    @cached_property
    def items_root(self) -> list[ItemsRootItemStrict]:
        return _load_model(ItemsRoot, list[ItemsRootItemStrict])

    @cached_property
    def item_by_id(self) -> dict[int, ItemsRootItem]:
        item_by_id: dict[int, ItemsRootItem] = {}
        for item in self.items_root:
            normalized_item = _coerce_item_root_item(item)
            if normalized_item is not None:
                item_by_id[normalized_item.id] = normalized_item
        return item_by_id

    @cache
    def get_item_effects_by_gid(self, item_id: int) -> list[ItemsRootItemEffect]:
        item = self.item_by_id[item_id]
        return [
            self.effect_instance_by_rid[possible_effect.rid]
            for possible_effect in (item.possibleEffects or [])
            if possible_effect.rid in self.effect_instance_by_rid
        ]

    @cached_property
    def effect_instance_by_rid(self) -> dict[int, ItemsRootItemEffect]:
        effect_item_entries = [
            entry for entry in self.items_root if entry.id is None and entry.effectId is not None
        ]
        min_rid = min(
            possible_effect.rid
            for item in self.item_by_id.values()
            for possible_effect in (item.possibleEffects or [])
        )
        return {
            min_rid + index: msgspec.convert(msgspec.to_builtins(entry), type=ItemsRootItemEffect)
            for index, entry in enumerate(effect_item_entries)
        }

    @cached_property
    def item_by_name(self) -> dict[str, ItemsRootItem]:
        _item_by_name: dict[str, ItemsRootItem] = {}
        for item in self.item_by_id.values():
            if not item.nameId or item.nameId not in I18N().name_by_id:
                continue
            _item_by_name[I18N().name_by_id[item.nameId]] = item
        return _item_by_name

    @cached_property
    def item_ids_by_type_id(self) -> dict[int, set[int]]:
        items = self.item_by_id.values()
        item_ids_by_type_id: dict[int, set[int]] = defaultdict(set)
        for item in items:
            if not item.typeId or not item.id:
                continue
            item_ids_by_type_id[item.typeId].add(item.id)
        return item_ids_by_type_id

    @cached_property
    def item_ids_by_category(self) -> dict[CategoryItemEnum, set[int]]:
        items = self.item_by_id.values()
        item_ids_by_category: dict[CategoryItemEnum, set[int]] = defaultdict(set)
        for item in items:
            if not item.typeId or not item.id:
                continue
            item_ids_by_category[CategoryItemEnum(self.item_type_by_id[item.typeId].categoryId)].add(item.id)
        return item_ids_by_category

    @cached_property
    def item_type_by_id(self) -> dict[int, ItemTypeData]:
        data = _load_model(ItemsTypeRoot, ItemsTypeRoot)
        return {item.id: item for item in data if item.id is not None}

    @cached_property
    def recipes(self) -> list[RecipeItem]:
        recipes = _load_model(RecipeRoot, RecipeRoot)
        return recipes

    @cached_property
    def recipe_by_result_id(self) -> dict[int, RecipeItem]:
        return {recipe.resultId: recipe for recipe in self.recipes}

    @cached_property
    def job_by_id(self) -> dict[int, JobsRootItem]:
        data = _load_model(JobsRoot, JobsRoot)
        return {job.id: job for job in data}

    @cached_property
    def map_info_by_map_id(self) -> dict[int, MapInformationRootItem]:
        data = _load_model(MapInformationsRoot, MapInformationsRoot)
        return {map_pos.id: map_pos for map_pos in data}

    @cached_property
    def map_pos_by_coord(self) -> dict[tuple[int, int], list[MapInformationRootItem]]:
        map_pos_by_coord_dict: dict[tuple[int, int], list[MapInformationRootItem]] = defaultdict(list)
        for map_pos in self.map_info_by_map_id.values():
            map_pos_by_coord_dict[(map_pos.posX, map_pos.posY)].append(map_pos)
        return map_pos_by_coord_dict

    @cached_property
    def sub_area_by_id(self) -> dict[int, SubAreasRootItem]:
        data = _load_model(SubAreasRoot, SubAreasRoot)
        return {sub_area.id: sub_area for sub_area in data}

    @cached_property
    def map_ids_by_sub_area_id(self) -> dict[int, list[int]]:
        map_ids_by_sub_area_id_dict: dict[int, list[int]] = {}
        for sub_area in self.sub_area_by_id.values():
            map_ids_by_sub_area_id_dict[sub_area.id] = sub_area.mapIds
        return map_ids_by_sub_area_id_dict

    @cached_property
    def area_by_id(self) -> dict[int, AreasRootItem]:
        data = _load_model(AreasRoot, AreasRoot)
        return {area.id: area for area in data}

    @cached_property
    def sub_areas_by_area_id(self) -> dict[int, set[int]]:
        sub_area_ids_by_area_id_dict: dict[int, set[int]] = defaultdict(set)
        for sub_area in self.sub_area_by_id.values():
            sub_area_ids_by_area_id_dict[sub_area.areaId].add(sub_area.id)
        return sub_area_ids_by_area_id_dict

    @cached_property
    def monsters_by_id(self) -> dict[int, MonsterItem]:
        data = _load_model(MonstersRoot, MonstersRoot)
        return {monster.id: monster for monster in data}

    @cached_property
    def monster_ids_by_name(self) -> dict[str, list[int]]:
        """Monster display name -> every monster carrying it."""
        monster_ids_by_name_dict: dict[str, list[int]] = defaultdict(list)
        for monster in self.monsters_by_id.values():
            name = I18N().name_by_id.get(monster.nameId)
            if name:
                monster_ids_by_name_dict[name].append(monster.id)
        return monster_ids_by_name_dict

    @cached_property
    def monsters_by_race(self) -> dict[int, list[MonsterItem]]:
        monsters_by_race_dict: defaultdict[int, list[MonsterItem]] = defaultdict(list)
        for monster in self.monsters_by_id.values():
            monsters_by_race_dict[monster.race].append(monster)
        return monsters_by_race_dict

    @cached_property
    def waypoint_by_id(self) -> dict[int, WaypointsRootItem]:
        data = _load_model(WaypointsRoot, WaypointsRoot)
        return {waypoint.id: waypoint for waypoint in data}

    @cached_property
    def skill_by_id(self) -> dict[int, SkillsRootItem]:
        data = _load_model(SkillsRoot, SkillsRoot)
        return {skill.id: skill for skill in data}

    @cached_property
    def gathered_item_ids(self) -> set[int]:
        return {
            skill.gatheredRessourceItem
            for skill in self.skill_by_id.values()
            if skill.parentJobId in HARVESTER_JOB_IDS and skill.gatheredRessourceItem not in [-1, 0]
        }

    @cached_property
    def quest_by_id(self) -> dict[int, QuestsRootItem]:
        data = _load_model(QuestsRoot, QuestsRoot)
        return {quest.id: quest for quest in data}

    @cached_property
    def quest_objective_by_id(self) -> dict[int, QuestObjectivesRootItem]:
        data = _load_model(QuestObjectivesRoot, QuestObjectivesRoot)
        return {quest_obj.id: quest_obj for quest_obj in data}

    @cached_property
    def quest_step_by_id(self) -> dict[int, QueststepsrootItem]:
        data = _load_model(Queststepsroot, Queststepsroot)
        return {quest_step.id: quest_step for quest_step in data}

    @cached_property
    def quest_objective_ids_by_step_id(self) -> dict[int, list[int]]:
        return {step.id: step.objectiveIds for step in self.quest_step_by_id.values()}

    @cached_property
    def spell_by_id(self) -> dict[int, SpellsRootItem]:
        data = _load_model(SpellsRoot, SpellsRoot)
        return {spell.id: spell for spell in data}

    @cached_property
    def effect_by_id(self) -> dict[int, EffectsRootItem]:
        data = _load_model(EffectsRoot, EffectsRoot)
        return {effect.id: effect for effect in data}

    @cached_property
    def characteristic_by_id(self) -> dict[int, CharacteristicsRootItem]:
        data = _load_model(CharacteristicsRoot, CharacteristicsRoot)
        return {characteristic.id: characteristic for characteristic in data}

    @cached_property
    def spell_variants(self) -> SpellVariantsRoot:
        spell_variants = _load_model(SpellVariantsRoot, SpellVariantsRoot)
        return spell_variants

    @cached_property
    def breed_by_id(self) -> dict[int, BreedsrootItem]:
        breeds = _load_model(Breedsroot, Breedsroot)
        return {breed.id: breed for breed in breeds}

    @cached_property
    def spell_variant_by_breed_id(self) -> dict[int, list[SpellVariantsRootItem]]:
        _spell_variant_by_breed_id: dict[int, list[SpellVariantsRootItem]] = defaultdict(list)
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
    def spell_lvl_by_id(self) -> dict[int, SpellLevelsRootItem]:
        data = _load_model(SpellLevelsRoot, SpellLevelsRoot)
        return {elem.id: elem for elem in data}

    @cached_property
    def spell_lvl_by_spell_id(self) -> dict[int, list[SpellLevelsRootItem]]:
        spell_levels_by_spell_id: dict[int, list[SpellLevelsRootItem]] = defaultdict(list)
        for spell_lvl in self.spell_lvl_by_id.values():
            spell_levels_by_spell_id[spell_lvl.spellId].append(spell_lvl)
            spell_levels_by_spell_id[spell_lvl.spellId].sort(key=lambda spell_lvl: spell_lvl.minPlayerLevel)

        return spell_levels_by_spell_id

    @cached_property
    def dungeon_by_id(self) -> dict[int, DungeonsRootItem]:
        data = _load_model(DungeonsRoot, DungeonsRoot)
        return {dungeon.id: dungeon for dungeon in data}

    @cached_property
    def dungeon_by_entrance_map_id(self) -> dict[int, DungeonsRootItem]:
        return {
            dungeon.entranceMapId: dungeon
            for dungeon in self.dungeon_by_id.values()
            if len(dungeon.mapIds) > _MIN_DUNGEON_MAP_COUNT
        }

    @cached_property
    def npc_action_by_id(self) -> dict[int, NpcActionsRootItem]:
        data = _load_model(NpcActionsRoot, NpcActionsRoot)
        return {npc_action.id: npc_action for npc_action in data}

    @cached_property
    def npc_messages_by_id(self) -> dict[int, NpcMessagesRootItem]:
        data = _load_model(NpcMessagesRoot, NpcMessagesRoot)
        return {npc_msg.id: npc_msg for npc_msg in data}

    @cached_property
    def npc_by_id(self) -> dict[int, NpcsRootItem]:
        data = _load_model(NpcsRoot, NpcsRoot)
        return {npc.id: npc for npc in data}

    @cached_property
    def npc_ids_by_name(self) -> dict[str, list[int]]:
        """Npc display name -> every npc carrying it; ~380 names are shared, hence the list."""
        npc_ids_by_name_dict: dict[str, list[int]] = defaultdict(list)
        for npc in self.npc_by_id.values():
            name = I18N().name_by_id.get(npc.nameId)
            if name:
                npc_ids_by_name_dict[name].append(npc.id)
        return npc_ids_by_name_dict

    @cached_property
    def npc_reply_i18n_by_reply_id(self) -> dict[int, int]:
        """`reply_id` -> i18n id. Reply ids are globally unique, so no npc scoping is needed."""
        i18n_by_reply_id: dict[int, int] = {}
        for npc in self.npc_by_id.values():
            for dialog_reply in npc.dialogReplies:
                reply_id, i18n_id = dialog_reply.values
                i18n_by_reply_id[reply_id] = i18n_id
        return i18n_by_reply_id

    @cached_property
    def npc_message_i18n_by_message_id(self) -> dict[int, int]:
        """`NpcDialogQuestionEvent.message_id` -> i18n id of the question text."""
        i18n_by_message_id: dict[int, int] = {}
        for npc in self.npc_by_id.values():
            for dialog_message in npc.dialogMessages:
                message_id, i18n_id = dialog_message.values
                i18n_by_message_id[message_id] = i18n_id
        return i18n_by_message_id

    @cached_property
    def npc_reply_ids_by_npc_id(self) -> dict[int, list[int]]:
        """Every reply an npc can ever offer."""
        return {
            npc.id: [dialog_reply.values[0] for dialog_reply in npc.dialogReplies]
            for npc in self.npc_by_id.values()
        }

    @cached_property
    def npc_replies_id_by_i18n(self) -> dict[int, list[int]]:
        replies_by_i18n: dict[int, list[int]] = defaultdict(list)
        for npc in self.npc_by_id.values():
            for dialog_msg in npc.dialogMessages:
                reply_id, i18n = dialog_msg.values
                replies_by_i18n[i18n].append(reply_id)
        return replies_by_i18n

    @staticmethod
    @cache
    def get_all_map_ids() -> set[int]:
        map_pos_ids = set(DataReader().map_info_by_map_id)
        map_bundle_ids = {
            int(path.stem.split("map_")[1])
            for path in MAP_BUNDLES_ROOT.iterdir()
            if path.is_file() and path.suffix == ".json" and path.stem.startswith("map_")
        }
        return map_pos_ids | map_bundle_ids | WorldGraphReader().get_all_transition_map_ids

    @staticmethod
    @cache
    def get_all_sub_area_ids() -> set[int]:
        return set(DataReader().sub_area_by_id)

    @staticmethod
    @cache
    def get_all_skill_ids() -> set[int]:
        return set(DataReader().skill_by_id)

    @staticmethod
    @cache
    def get_all_characteristic_ids() -> set[int]:
        return set(DataReader().characteristic_by_id)

    @staticmethod
    @cache
    def get_all_item_ids() -> set[int]:
        return set(DataReader().item_by_id)

    @staticmethod
    @cache
    def get_all_monster_gids() -> set[int]:
        return set(DataReader().monsters_by_id)

    @staticmethod
    @cache
    def get_all_spell_ids() -> set[int]:
        return set(DataReader().spell_by_id)

    @staticmethod
    @cache
    def get_all_spell_lvl_ids() -> set[int]:
        return set(DataReader().spell_lvl_by_id)

    @staticmethod
    @cache
    def get_all_type_item_ids() -> set[int]:
        return {item.typeId for item in DataReader().item_by_id.values() if item.typeId}

    @staticmethod
    @cache
    def get_all_job_ids() -> set[int]:
        return set(DataReader().job_by_id) | {79}

    @staticmethod
    @cache
    def get_all_x_world_coodinates() -> set[int]:
        return {x for x, _ in DataReader().map_pos_by_coord}

    @staticmethod
    @cache
    def get_all_y_world_coodinates() -> set[int]:
        return {y for _, y in DataReader().map_pos_by_coord}

    @staticmethod
    @cache
    def get_all_key_cells() -> set[int]:
        key_cells: set[int] = set()
        for cell_id in range(560 + 1):
            for direction in range(8):
                key_cells.add(cell_id | direction << 12)
        return key_cells
