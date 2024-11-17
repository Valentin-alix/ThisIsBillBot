from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Database.enums.jobs_enum import HARVESTER_JOB_IDS, JobEnum
from D3Database.models.datas.recipe_root import RecipeItem
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.controller.sale_hotel import SaleHotelController
from src.core.config import WEIGHT_BY_JOB
from src.core.engine.items.item import GATHERER_ITEM_GIDS
from src.core.engine.items.item_type import ItemTypeEnum
from src.core.game_constants import MAP_ID_BY_SKILL_ID
from src.core.states.guild_chest_state import GIDS_BY_TAB
from src.services.logging.logger import Logger


def get_benefice_on_craft_recipe(recipe: RecipeItem) -> tuple[float, float]:
    avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()
    if recipe.resultId in avg_price_by_gid and all(
        ingredient_id in avg_price_by_gid for ingredient_id in recipe.ingredientIds
    ):
        profit = avg_price_by_gid[recipe.resultId]
        for ingredient_id in recipe.ingredientIds:
            profit -= avg_price_by_gid[ingredient_id]
        return profit, profit / avg_price_by_gid[recipe.resultId]
    return 0, 0


def is_not_valid_recipe_for_lvl_up_job_or_benefice(
    recipe: RecipeItem, is_sub: bool, jobs_lvl_by_id: dict[int, int]
) -> bool:
    max_job_lvl = 200 if is_sub else 60
    current_job_lvl = jobs_lvl_by_id.get(recipe.jobId)
    if current_job_lvl is None or current_job_lvl >= max_job_lvl:
        # insufficient lvl
        return True
    if recipe.skillId not in MAP_ID_BY_SKILL_ID:
        # not configured craft
        return True
    result_item = DataReader().item_by_id[recipe.resultId]
    if result_item.craftConditional not in ["", None]:
        # the item need a condition, like a quest completed or something
        return True
    if recipe.jobId not in HARVESTER_JOB_IDS and recipe.jobId != JobEnum.CHASSEUR:
        return True
    benefit_percent = get_benefice_on_craft_recipe(recipe)[1]
    if current_job_lvl - recipe.resultLevel >= 20 and not (
        benefit_percent > 0.3 and recipe.resultId in GIDS_BY_TAB[2]
    ):
        # this recipe don't give enought xp, skip
        return True
    if any(
        (
            ingredient_id not in GATHERER_ITEM_GIDS
            and DataReader().item_by_id[ingredient_id].typeId != ItemTypeEnum.VIANDE
        )
        for ingredient_id in recipe.ingredientIds
    ):
        # recipe contains an ingredient that we can't gather, skip
        return True
    return False


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


FORBIDDEN_CRAFT_IDS: set[int] = {60}


def get_valid_recipes(
    logger: Logger, jobs_lvl_by_id: dict[int, int], recipes: list[RecipeItem]
) -> list[RecipeItem]:
    """
    Filter recipes based on job level requirements and forbidden crafts.

    This is the canonical implementation - states should delegate to this function.
    """
    valid_recipes = []
    for recipe in recipes:
        # Filter forbidden crafts
        if recipe.resultId in FORBIDDEN_CRAFT_IDS:
            continue

        skill_data = DataReader().skill_by_id[recipe.skillId]
        if jobs_lvl_by_id.get(skill_data.parentJobId, 1) < recipe.resultLevel:
            result_name = I18N().name_by_id.get(
                int(recipe.resultNameId), str(recipe.resultId)
            )
            logger.warning(f"Can't craft recipe {result_name} because of job lvl")
            continue
        valid_recipes.append(recipe)
    return valid_recipes


def get_recipes_for_job_lvl_upor_benefice(is_sub: bool, jobs_lvl_by_id: dict[int, int]):
    recipes: list[RecipeItem] = []
    for recipe in DataReader().recipes:
        if is_not_valid_recipe_for_lvl_up_job_or_benefice(
            recipe, is_sub, jobs_lvl_by_id
        ):
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
