import os
from typing import Any

from tqdm import tqdm

from db_dofus_unity.generator.struct import gen_model
from models.datas.dungeons_root import DungeonsRoot
from models.datas.npc_actions_root import NpcActionsRoot
from models.datas.npc_messages_root import NpcMessagesRoot
from models.datas.npcs_root import NpcsRoot


from db_dofus_unity.generator.i18n import I18NReader

from D3Database.models.datas.areas_root import AreasRoot
from D3Database.models.datas.characteristic_category_root import (
    CharacteristicCategoriesRoot,
)
from D3Database.models.datas.characteristic_root import CharacteristicsRoot
from D3Database.models.datas.effects_root import EffectsRoot
from D3Database.models.datas.item_type_root import ItemsTypeRoot
from D3Database.models.datas.items_root import ItemsRoot
from D3Database.models.datas.jobs_root import JobsRoot
from D3Database.models.datas.map_positions_root import MapPositionsRoot
from D3Database.models.datas.monsters_root import MonstersRoot
from D3Database.models.datas.quest_objectives_root import QuestObjectivesRoot
from D3Database.models.datas.quests_root import QuestsRoot
from D3Database.models.datas.recipe_root import RecipeRoot
from D3Database.models.datas.skills_root import SkillsRoot
from D3Database.models.datas.spell_levels_root import SpellLevelsRoot
from D3Database.models.datas.spell_variants_root import SpellVariantsRoot
from D3Database.models.datas.spells_root import SpellsRoot
from D3Database.models.datas.sub_areas_root import SubAreasRoot
from D3Database.models.datas.waypoints_root import WaypointsRoot
from D3Database.models.maps import MapDataRoot
from D3Database.models.world_graph import WorldGraphData
from db_dofus_unity.generator.data_cleaning import clean_data_to_output


from db_dofus_unity.consts import (
    PATH_DATAS,
    PATH_MAPS,
    PATH_STANDALONE_BUNDLES,
    UABEA_PATH_EXE,
)
from D3Database.consts import (
    D3_STANDALONE,
    D3_MAP,
    D3_DATA,
    OUTPUT_CLASS_DATAS,
)


def get_world_graph_datas():
    print("get world graph")
    bundle_filename = next(
        filename
        for filename in os.listdir(PATH_STANDALONE_BUNDLES)
        if "worldassets_assets_all" in filename
    )
    os.system(
        f"{UABEA_PATH_EXE} batchexportbundle {os.path.join(PATH_STANDALONE_BUNDLES, bundle_filename)} -out {D3_STANDALONE}"
    )

    print("cleaning worldgraph")
    for filename in os.listdir(D3_STANDALONE):
        if filename == "world-graph.json":
            clean_data_to_output(WorldGraphData, os.path.join(D3_STANDALONE, filename))
        else:
            os.remove(os.path.join(D3_STANDALONE, filename))


def get_map_datas() -> None:
    print("get maps")

    # init last modified time
    last_modified_by_filename: dict[str, float] = {}
    for filename in os.listdir(D3_MAP):
        filepath = os.path.join(D3_MAP, filename)
        last_modified_by_filename[filename] = os.path.getmtime(filepath)

    treated_filenames: set[str] = set()
    map_bundles = {
        filename
        for filename in os.listdir(PATH_MAPS)
        if "mapdata_assets_world" in filename and filename.endswith(".bundle")
    }
    for filename in tqdm(map_bundles):
        bundle_path = os.path.join(PATH_MAPS, filename)
        os.system(f"{UABEA_PATH_EXE} batchexportbundle {bundle_path} -out {D3_MAP}")
        for out_filename in set(os.listdir(D3_MAP)) - treated_filenames:
            if not (out_filename.endswith(".json") and out_filename.startswith("map_")):
                continue
            out_filepath = os.path.join(D3_MAP, out_filename)
            last_modified = last_modified_by_filename.get(out_filename)
            if last_modified and last_modified == os.path.getmtime(out_filepath):
                continue
            clean_data_to_output(MapDataRoot, out_filepath)
            treated_filenames.add(out_filename)


def get_datas() -> None:
    print("get content data")
    model_by_data_name_pattern: dict[str, Any] = {
        "itemsroot": ItemsRoot,
        "jobsroot": JobsRoot,
        "mappositionsroot": MapPositionsRoot,
        "subareasroot": SubAreasRoot,
        "areasroot": AreasRoot,
        "waypointsroot": WaypointsRoot,
        "skillsroot": SkillsRoot,
        "questsroot": QuestsRoot,
        "questobjectivesroot": QuestObjectivesRoot,
        "spellsroot": SpellsRoot,
        "spellvariantsroot": SpellVariantsRoot,
        "spelllevelsroot": SpellLevelsRoot,
        "effectsroot": EffectsRoot,
        "characteristicsroot": CharacteristicsRoot,
        "characteristiccategoriesroot": CharacteristicCategoriesRoot,
        "recipesroot": RecipeRoot,
        "itemtypesroot": ItemsTypeRoot,
        "monstersroot": MonstersRoot,
        "dungeonsroot": DungeonsRoot,
        "npcsroot": NpcsRoot,
        "npcmessagesroot": NpcMessagesRoot,
        "npcactionsroot": NpcActionsRoot,
    }
    for filename in tqdm(os.listdir(PATH_DATAS)):
        infos = next(
            (
                (short_filename, model)
                for short_filename, model in model_by_data_name_pattern.items()
                if f"data_assets_{short_filename}.asset.bundle" == filename
            ),
            None,
        )
        if infos is None:
            continue
            if "data_assets_" not in filename:
                continue
            short_filename = filename.split(".asset")[0].split("data_assets_")[1]
            related_model = None
        else:
            short_filename, related_model = infos

        command = f"{UABEA_PATH_EXE} batchexportbundle {os.path.join(PATH_DATAS, filename)} -out {D3_DATA}"
        os.system(command)
        filepath = f"{os.path.join(D3_DATA, short_filename)}.json"
        if related_model is None:
            gen_model(D3_DATA, short_filename + ".json", OUTPUT_CLASS_DATAS)
            continue
        clean_data_to_output(related_model, filepath)


def update_all_datas():
    get_datas()
    get_world_graph_datas()
    I18NReader.get_datas()
    get_map_datas()


if __name__ == "__main__":
    get_datas()
