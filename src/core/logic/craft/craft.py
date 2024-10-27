from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from enums.jobs_enum import HARVESTER_JOB_IDS, JobEnum
from models.datas.recipe_root import RecipeItem

from src.common.logger import Logger
from src.core.config.storage import GATHERER_ITEM_GIDS
from src.core.config.weights import WEIGHT_BY_JOB
from src.interfaces.enums.item_type_enum import ItemTypeEnum

MAP_ID_BY_SKILL_ID: dict[int, set[int]] = {
    101: {217063430, 192940034},
    23: {217057284, 192937988},
    48: {217061380, 192939010},
    32: {217060356, 192939010},
    47: {217061382, 192939008},
    27: {217061382, 192939008},
    135: {217062406, 192937984},
    134: {192937994},  # chasseur
}


def get_valid_recipes(
    logger: Logger, jobs_lvl_by_id: dict[int, int], recipes: list[RecipeItem]
) -> list[RecipeItem]:
    valid_recipes = []
    for recipe in recipes:
        skill_data = DataReader().skill_by_id[recipe.skillId]
        if jobs_lvl_by_id.get(skill_data.parentJobId, 1) < recipe.resultLevel:
            logger.warning(f"Can't craft recipe {recipe} because of job lvl")
            continue
        valid_recipes.append(recipe)
    return valid_recipes


def get_recipes_for_job_lvl_up(is_sub: bool, jobs_lvl_by_id: dict[int, int]):
    recipes: list[RecipeItem] = []
    for recipe in DataReader().recipes:
        if is_not_valid_recipe_for_lvl_up_job(recipe, is_sub, jobs_lvl_by_id):
            continue
        recipes.append(recipe)
    recipes.sort(
        key=lambda recipe: (
            WEIGHT_BY_JOB.get(JobEnum(recipe.jobId), 1),
            recipe.resultLevel - jobs_lvl_by_id[recipe.jobId],
        ),
        reverse=True,
    )
    return recipes


def is_not_valid_recipe_for_lvl_up_job(
    recipe: RecipeItem, is_sub: bool, jobs_lvl_by_id: dict[int, int]
) -> bool:
    max_job_lvl = 200 if is_sub else 60
    current_job_lvl = jobs_lvl_by_id.get(recipe.jobId)
    return (
        current_job_lvl is None
        or current_job_lvl >= max_job_lvl
        or recipe.skillId not in MAP_ID_BY_SKILL_ID
        or (recipe.jobId not in HARVESTER_JOB_IDS and recipe.jobId != JobEnum.CHASSEUR)
        or current_job_lvl - recipe.resultLevel >= 20
        or any(
            (
                ingredient_id not in GATHERER_ITEM_GIDS
                and DataReader().item_by_id[ingredient_id].typeId != ItemTypeEnum.VIANDE
            )
            for ingredient_id in recipe.ingredientIds
        )
    )


def get_max_result_quantity(
    logger: Logger,
    storage_object_by_gid: dict[int, ObjectItemInventory],
    recipe: RecipeItem,
) -> tuple[int, int]:
    max_result_quantity: int | None = None
    weight_for_one_result = 0

    for ingredient_id, quantity in zip(recipe.ingredientIds, recipe.quantities):
        ingredient_in_chest = storage_object_by_gid.get(ingredient_id)
        if ingredient_in_chest is None:
            name_id = DataReader().item_by_id[ingredient_id].nameId
            logger.info(
                f"ingredient {I18N().name_by_id[name_id] if name_id else ''} not in chest, can't "
                f"craft recipe"
            )
            logger.info(
                f"we have {list(storage_object_by_gid.keys())} gids and we need this : {ingredient_id}"
            )
            return 0, weight_for_one_result
        if ingredient_in_chest.item.quantity < quantity:
            name_id = DataReader().item_by_id[ingredient_id].nameId
            logger.info(
                f"ingredient {I18N().name_by_id[name_id] if name_id else ''} don't have enough "
                f"quantity, can't craft recipe {I18N().name_by_id[int(recipe.resultNameId)]}"
            )
            return 0, weight_for_one_result

        result_quantity = ingredient_in_chest.item.quantity // quantity
        if max_result_quantity is None or result_quantity < max_result_quantity:
            max_result_quantity = result_quantity

        weight_for_one_result += quantity * (
            DataReader().item_by_id[ingredient_id].realWeight or 0
        )

    return (max_result_quantity or 0), weight_for_one_result


def get_max_possible_result_quantity(
    weight_max: int,
    inventory_weight: int,
    weight_for_one_result: int,
    max_result_quantity: int,
):
    player_weight = weight_max - inventory_weight
    max_possible_result_quantity = min(
        player_weight // weight_for_one_result,
        max_result_quantity,  # type: ignore
    )
    return max_possible_result_quantity


if __name__ == "__main__":
    for recipe in get_recipes_for_job_lvl_up(False, {JobEnum.CHASSEUR: 40}):
        print(I18N().name_by_id[int(recipe.resultNameId)])
