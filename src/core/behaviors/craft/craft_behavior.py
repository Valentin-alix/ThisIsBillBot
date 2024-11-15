from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial
from typing import Callable

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeCraftCountModifiedEvent,
    ExchangeCraftCountRequest,
    ExchangeCraftStartedEvent,
    ExchangeLeaveEvent,
    ExchangeReadyRequest,
    ExchangeSetCraftRecipeRequest,
)
from d3_mapping.resources.protos.game.inventory_pb2 import InventoryWeightEvent
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from data_center.map_reader import MapReader
from grid.map_point import MapPoint
from models.datas.recipe_root import RecipeItem

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.loads.load_recipe_from_bank_chest_behavior import (
    LoadRecipeFromBankChestBehavior,
)
from src.core.behaviors.storage.loads.load_recipe_from_guild_chest_behavior import (
    LoadRecipeFromGuildChestBehavior,
)
from src.core.config.timings import BASE_RANGE, SMALL_RANGE
from src.core.logic.craft.craft import MAP_ID_BY_SKILL_ID
from src.core.logic.map.map_tools import MapTools
from src.core.logic.map.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException


class CraftErrorCode(StrEnum):
    CRAFT_TIMEOUT = auto()


FORBIDDEN_CRAFT_IDS: set[int] = {60}


@dataclass
class CraftBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    load_recipe_from_guild_chest_behavior: LoadRecipeFromGuildChestBehavior
    load_recipe_from_bank_chest_behavior: LoadRecipeFromBankChestBehavior
    interactive_behavior: InteractiveBehavior
    pathfinding: Pathfinding

    _stop_craft_recipe_condition: Callable[[RecipeItem], bool] | None = field(
        init=False, default=None
    )
    _remaining_recipes: list[RecipeItem] = field(init=False, default_factory=list)
    _loaded_recipes_infos: list[tuple[RecipeItem, int]] = field(
        init=False, default_factory=list
    )

    def run(
        self,
        recipes: list[RecipeItem],
        stop_craft_recipe_condition: Callable[[RecipeItem], bool] | None = None,
    ) -> None:
        self._remaining_recipes = self.get_valid_recipes(recipes)
        self._stop_craft_recipe_condition = stop_craft_recipe_condition
        self.process_remaining_recipes()

    def get_valid_recipes(
        self,
        recipes: list[RecipeItem],
    ) -> list[RecipeItem]:
        valid_recipes = []
        for recipe in recipes:
            if recipe.resultId in FORBIDDEN_CRAFT_IDS:
                continue
            skill_data = DataReader().skill_by_id[recipe.skillId]
            if (
                self.game_state.player.jobs_lvl_by_id.get(skill_data.parentJobId, 1)
                < recipe.resultLevel
            ):
                self.logger.warning(
                    f"Can't craft recipe {I18N().name_by_id[int(recipe.resultNameId)]} because of job lvl"
                )
                continue
            valid_recipes.append(recipe)
        return valid_recipes

    def process_remaining_recipes(self):
        self.logger.info(
            f"{len(self._remaining_recipes)} before filtering by conditon "
        )
        self._remaining_recipes = [
            recipe
            for recipe in self._remaining_recipes
            if (
                not self._stop_craft_recipe_condition
                or not self._stop_craft_recipe_condition(recipe)
            )
        ]
        self.logger.info(f"{len(self._remaining_recipes)} after filtering by conditon ")

        if len(self._remaining_recipes) == 0:
            return self.finish()

        if self.game_state.player.is_sub:
            self.load_recipe_from_guild_chest_behavior.start(
                callback=self.on_load_from_chest_behavior_finished,
                parent=self,
                recipes=self._remaining_recipes,
            )
        else:
            self.load_recipe_from_bank_chest_behavior.start(
                callback=self.on_load_from_chest_behavior_finished,
                parent=self,
                recipes=self._remaining_recipes,
            )

    def on_load_from_chest_behavior_finished(
        self,
        error_code: str | None,
        loaded_recipes_infos: list[tuple[RecipeItem, int]],
        remaining_recipes: list[RecipeItem],
    ):
        if error_code is not None:
            return self.finish(error_code)

        if len(loaded_recipes_infos) == 0:
            return self.finish()

        self._remaining_recipes = remaining_recipes
        self._loaded_recipes_infos = loaded_recipes_infos

        self.process_next_loaded_recipe_skill()

    def process_next_loaded_recipe_skill(self):
        if len(self._loaded_recipes_infos) == 0:
            return self.process_remaining_recipes()

        target_skill_id = self._loaded_recipes_infos[0][0].skillId
        target_recipes_infos = [
            recipe_info
            for recipe_info in self._loaded_recipes_infos
            if recipe_info[0].skillId == target_skill_id
        ]
        self._loaded_recipes_infos = [
            recipe_info
            for recipe_info in self._loaded_recipes_infos
            if recipe_info[0].skillId != target_skill_id
        ]
        self.go_and_craft_on_skill(target_recipes_infos, target_skill_id)

    def go_and_craft_on_skill(
        self, recipes_infos: list[tuple[RecipeItem, int]], skill_id: int
    ):
        related_map_ids = MAP_ID_BY_SKILL_ID[skill_id]
        if not self.game_state.player.is_sub:
            related_map_ids = {
                map_id
                for map_id in related_map_ids
                if MapTools.is_map_allowed_for_unsub(map_id)
            }
        if len(related_map_ids) == 0:
            self.logger.warning(
                f"Did not found any related map for the skill {skill_id}"
            )
            for recipe, _ in recipes_infos:
                self._remaining_recipes.remove(recipe)
            return self.process_remaining_recipes()

        self.run_timer(
            BASE_RANGE,
            lambda: self.auto_trip_smart_behavior.start(
                map_ids=related_map_ids,
                callback=partial(
                    self.on_auto_trip_smart_behavior_to_workshop_finished,
                    recipes_infos=recipes_infos,
                    skill_id=skill_id,
                ),
                parent=self,
            ),
        )

    def on_auto_trip_smart_behavior_to_workshop_finished(
        self,
        error_code: str | None,
        recipes_infos: list[tuple[RecipeItem, int]],
        skill_id: int,
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        related_element, related_skill = next(
            (element, skill)
            for element in self.game_state.interactive.interactive_element_by_id.values()
            if (
                skill := next(
                    (
                        enabled_skill
                        for enabled_skill in element.enabled_skills
                        if enabled_skill.skill_id == skill_id
                    ),
                    None,
                )
            )
            is not None
        )
        element_mp = MapPoint.from_cell_id(
            MapReader()
            .get_ref_data_by_element_id_by_map_id(self.game_state.map.map_id)[
                related_element.element_id
            ]
            .cellId  # type: ignore
        )
        move_path = self.pathfinding.find_path(
            self.game_state.player.map_point, {element_mp}
        )

        self.run_timer(
            BASE_RANGE,
            lambda: self.interactive_behavior.start(
                move_path=move_path,
                element_id=related_element.element_id,
                skill_instance_uid=related_skill.skill_instance_uid,
                callback=partial(
                    self.on_interactive_behavior_finished,
                    recipes_infos=recipes_infos,
                ),
                parent=self,
            ),
        )

    def on_interactive_behavior_finished(
        self, error_code: str | None, recipes_infos: list[tuple[RecipeItem, int]]
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.event_manager.on(
            ExchangeCraftStartedEvent,
            partial(self.on_exchange_craft_started_event, recipes_infos=recipes_infos),
            originator=self,
            once=True,
        )

    def on_exchange_craft_started_event(
        self,
        msg: ExchangeCraftStartedEvent,
        recipes_infos: list[tuple[RecipeItem, int]],
    ):
        self.craft_recipe_in_same_skill(recipes_infos)

    def craft_recipe_in_same_skill(self, recipes_infos: list[tuple[RecipeItem, int]]):
        if len(recipes_infos) == 0:
            return self.on_all_crafted_for_skill_in_inventory()

        recipe, max_possible_result_quantity = recipes_infos.pop()
        self.logger.info(
            f"Gonna craft {I18N().name_by_id[int(recipe.resultNameId)]} for quantity {max_possible_result_quantity}"
        )
        self.event_manager.on(
            ExchangeSetCraftRecipeRequest,
            partial(
                self.on_exchange_set_craft_recipe_request,
                recipes_infos=recipes_infos,
                max_possible_result_quantity=max_possible_result_quantity,
                gid=recipe.resultId,
            ),
            once=True,
            originator=self,
        )

        req = ExchangeSetCraftRecipeRequest(object_uid=recipe.resultId)
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))

    def on_exchange_set_craft_recipe_request(
        self,
        msg: ExchangeSetCraftRecipeRequest,
        recipes_infos: list[tuple[RecipeItem, int]],
        max_possible_result_quantity: int,
        gid: int,
    ):
        self.event_manager.clear_modifier_by_origin_and_type(DialogLeaveRequest, self)
        self.event_manager.on(
            ExchangeCraftCountModifiedEvent,
            partial(
                self.on_exchange_craft_count_modified_event,
                recipes_infos=recipes_infos,
                gid=gid,
            ),
            originator=self,
            once=True,
        )
        self.run_timer(
            BASE_RANGE,
            lambda: self.event_manager.send(
                ExchangeCraftCountRequest(count=max_possible_result_quantity)
            ),
        )

    def on_exchange_craft_count_modified_event(
        self,
        msg: ExchangeCraftCountModifiedEvent,
        recipes_infos: list[tuple[RecipeItem, int]],
        gid: int,
    ):
        self.event_manager.on(
            InventoryWeightEvent,
            lambda _: self.craft_recipe_in_same_skill(recipes_infos),
            originator=self,
            once=True,
            timeout=15,
            on_timeout=lambda: self.on_timeout_exchange_ready(gid),
        )
        req = ExchangeReadyRequest(ready=True, step=6)
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_all_crafted_for_skill_in_inventory(self):
        self.event_manager.on(
            ExchangeLeaveEvent,
            lambda _: self.process_next_loaded_recipe_skill(),
            originator=self,
            once=True,
        )
        self.run_timer(
            SMALL_RANGE, lambda: self.event_manager.send(DialogLeaveRequest())
        )

    def on_timeout_exchange_ready(self, gid: int):
        self.event_manager.on(
            ExchangeLeaveEvent,
            lambda _: self.finish(),
            originator=self,
            once=True,
        )
        FORBIDDEN_CRAFT_IDS.add(gid)
        self.run_timer(
            SMALL_RANGE, lambda: self.event_manager.send(DialogLeaveRequest())
        )
