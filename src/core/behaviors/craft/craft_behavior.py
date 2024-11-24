from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial
from typing import Callable

from d3_database.data_center.i18n import I18N
from d3_database.data_center.map_reader import MapReader
from d3_database.grid.map_point import MapPoint
from d3_database.models.datas.recipe_root import RecipeItem
from d3_database.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from d3_database.protos.non_obf.game.exchange_pb2 import (
    ExchangeCraftCountModifiedEvent,
    ExchangeCraftCountRequest,
    ExchangeCraftStartedEvent,
    ExchangeReadyRequest,
    ExchangeSetCraftRecipeRequest,
)
from d3_database.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)

from src.core.behaviors.dialog_handler_behavior import DialogHandlerBehavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.loads.load_recipe_behavior import LoadRecipeBehavior
from src.core.config import BASE_RANGE, SMALL_RANGE
from src.core.engine.crafts.recipes import FORBIDDEN_CRAFT_IDS
from src.core.engine.movements.map.map_tools import MapTools
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.game_constants import Skills


class CraftErrorCode(StrEnum):
    CRAFT_TIMEOUT = auto()


@dataclass
class CraftBehavior(DialogHandlerBehavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    load_recipe_behavior: LoadRecipeBehavior
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
        self._remaining_recipes = self.game_state.craft.get_valid_recipes(recipes)
        self._stop_craft_recipe_condition = stop_craft_recipe_condition
        self.process_remaining_recipes()

    def process_remaining_recipes(self):
        initial_count = len(self._remaining_recipes)
        self._remaining_recipes = [
            recipe
            for recipe in self._remaining_recipes
            if (
                not self._stop_craft_recipe_condition
                or not self._stop_craft_recipe_condition(recipe)
            )
        ]

        if len(self._remaining_recipes) == 0:
            filtered_count = initial_count - len(self._remaining_recipes)
            self.logger.info(
                f"No more recipe to process, filtered out {filtered_count} recipes by condition"
            )
            return self.finish()

        self.logger.info(f"Processing {len(self._remaining_recipes)} recipes")

        self.load_recipe_behavior.start(
            callback=self.on_load_recipe_behavior_finished,
            parent=self,
            recipes=self._remaining_recipes,
        )

    def on_load_recipe_behavior_finished(
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
        related_map_ids = Skills.MAP_BY_SKILL[skill_id]
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
        self.raise_if_error(error_code)

        related_element, related_skill = (
            self.game_state.interactive.get_element_and_skill_by_skill_id(skill_id)
        )
        element_mp = MapPoint.from_cell_id(
            MapReader()
            .get_ref_data_by_element_id_by_map_id(self.game_state.map.map_id)[
                related_element.element_id
            ]
            .cellId  # type: ignore
        )
        move_path = self.pathfinding.find_path(
            self.game_state.map.map_point, {element_mp}
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
        self.raise_if_error(error_code)

        self.event_manager.on(
            ExchangeCraftStartedEvent,
            partial(self.on_exchange_craft_started_event, recipes_infos=recipes_infos),
            originator=self,
            once=True,
            override_on_self=True,
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
        item_name = I18N().name_by_id[int(recipe.resultNameId)]
        self.logger.info(
            f"Crafting {item_name} x{max_possible_result_quantity} ({len(recipes_infos)} recipes remaining in queue)"
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
            override_on_self=True,
        )

        req = ExchangeSetCraftRecipeRequest(object_uid=recipe.resultId)
        self.send_message_delayed(req, BASE_RANGE)

    def on_exchange_set_craft_recipe_request(
        self,
        msg: ExchangeSetCraftRecipeRequest,
        recipes_infos: list[tuple[RecipeItem, int]],
        max_possible_result_quantity: int,
        gid: int,
    ):
        self.unregister_listener(DialogLeaveRequest)
        self.event_manager.on(
            ExchangeCraftCountModifiedEvent,
            partial(
                self.on_exchange_craft_count_modified_event,
                recipes_infos=recipes_infos,
                gid=gid,
            ),
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.send_message_delayed(
            ExchangeCraftCountRequest(count=max_possible_result_quantity),
            BASE_RANGE,
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
            override_on_self=True,
            timeout=15,
            on_timeout=lambda: self.on_timeout_exchange_ready(gid),
        )
        req = ExchangeReadyRequest(ready=True, step=6)
        self.send_message_delayed(req, SMALL_RANGE)

    def on_all_crafted_for_skill_in_inventory(self):
        self.leave_dialog(
            on_leave_callback=lambda _: self.process_next_loaded_recipe_skill()
        )

    def on_timeout_exchange_ready(self, gid: int):
        FORBIDDEN_CRAFT_IDS.add(gid)
        self.leave_dialog(on_leave_callback=lambda _: self.finish())
