from dataclasses import dataclass
from functools import partial

from models.datas.recipe_root import RecipeItem
from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeCraftStartedEvent,
    ExchangeSetCraftRecipeRequest,
    ExchangeCraftCountRequest,
    ExchangeCraftCountModifiedEvent,
    ExchangeReadyRequest,
    ExchangeLeaveEvent,
)
from d3_mapping.resources.protos.game.inventory_pb2 import InventoryWeightEvent
from src.const import BASE_RANGE, SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.load_recipe_from_guild_chest_behavior import (
    LoadRecipeFromGuildChestBehavior,
)
from data_center.data_reader import DataReader
from data_center.map_reader import MapReader
from grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException

MAP_ID_BY_SKILL_ID = {
    101: 217063430,
    23: 217057284,
    48: 217061380,
    32: 217060356,
    47: 217061382,
    27: 217061382,
    135: 217062406,
}


@dataclass
class CraftBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    load_recipe_from_guild_chest_behavior: LoadRecipeFromGuildChestBehavior
    interactive_behavior: InteractiveBehavior
    pathfinding: Pathfinding

    def run(self, recipes: list[RecipeItem]) -> None:
        self.process_recipe(self.get_valid_recipes(recipes))

    def get_valid_recipes(self, recipes: list[RecipeItem]) -> list[RecipeItem]:
        valid_recipes = []
        for recipe in recipes:
            skill_data = DataReader().skill_by_id[recipe.skillId]
            if (
                self.game_state.player.jobs_lvl_by_id.get(skill_data.parentJobId, 1)
                < recipe.resultLevel
            ):
                self.logger.warning(f"Can't craft recipe {recipe} because of job lvl")
                continue
            valid_recipes.append(recipe)
        return valid_recipes

    def process_recipe(self, recipes: list[RecipeItem]):
        if len(recipes) == 0:
            return self.finish()
        target_recipe = recipes[0]
        self.load_recipe_from_guild_chest_behavior.start(
            callback=partial(
                self.on_load_from_guild_chest_behavior_finished,
                target_recipe=target_recipe,
                recipes=recipes,
            ),
            parent=self,
            recipe=target_recipe,
        )

    def on_load_from_guild_chest_behavior_finished(
        self,
        error_code: str | None,
        max_possible_result_quantity: int,
        target_recipe: RecipeItem,
        recipes: list[RecipeItem],
    ):
        if max_possible_result_quantity == 0:
            recipes.remove(target_recipe)
            return self.process_recipe(recipes)
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.auto_trip_smart_behavior.start(
            map_ids={MAP_ID_BY_SKILL_ID[target_recipe.skillId]},
            callback=partial(
                self.on_auto_trip_smart_behavior_to_workshop_finished,
                target_recipe=target_recipe,
                max_possible_result_quantity=max_possible_result_quantity,
                recipes=recipes,
            ),
            parent=self,
        )

    def on_auto_trip_smart_behavior_to_workshop_finished(
        self,
        error_code: str | None,
        target_recipe: RecipeItem,
        max_possible_result_quantity: int,
        recipes: list[RecipeItem],
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
                        if enabled_skill.skill_id == target_recipe.skillId
                    ),
                    None,
                )
            )
            is not None
        )
        element_mp = MapPoint.from_cell_id(
            MapReader()
            .get_ref_data_by_element_id(self.game_state.map.map_id)[
                related_element.element_id
            ]
            .cellId  # type: ignore
        )
        move_path = self.pathfinding.find_path(
            self.game_state.player.map_point, {element_mp}
        )
        self.interactive_behavior.start(
            move_path=move_path,
            element_id=related_element.element_id,
            skill_instance_uid=related_skill.skill_instance_uid,
            callback=partial(
                self.on_interactive_behavior_finished,
                target_recipe=target_recipe,
                max_possible_result_quantity=max_possible_result_quantity,
                recipes=recipes,
            ),
            parent=self,
        )

    def on_interactive_behavior_finished(
        self,
        error_code: str | None,
        target_recipe: RecipeItem,
        max_possible_result_quantity: int,
        recipes: list[RecipeItem],
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.event_manager.on(
            ExchangeCraftStartedEvent,
            partial(
                self.on_exchange_craft_started_event,
                target_recipe=target_recipe,
                max_possible_result_quantity=max_possible_result_quantity,
                recipes=recipes,
            ),
            originator=self,
            once=True,
        )

    def on_exchange_craft_started_event(
        self,
        msg: ExchangeCraftStartedEvent,
        target_recipe: RecipeItem,
        max_possible_result_quantity: int,
        recipes: list[RecipeItem],
    ):
        self.event_manager.on(
            ExchangeSetCraftRecipeRequest,
            partial(
                self.on_exchange_set_craft_recipe_request,
                max_possible_result_quantity=max_possible_result_quantity,
                recipes=recipes,
            ),
            once=True,
            originator=self,
        )

        req = ExchangeSetCraftRecipeRequest(object_uid=target_recipe.resultId)
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))

    def on_exchange_set_craft_recipe_request(
        self,
        msg: ExchangeSetCraftRecipeRequest,
        max_possible_result_quantity: int,
        recipes: list[RecipeItem],
    ):
        self.event_manager.clear_modifier_by_origin_and_type(DialogLeaveRequest, self)
        self.event_manager.on(
            ExchangeCraftCountModifiedEvent,
            partial(self.on_exchange_craft_count_modified_event, recipes=recipes),
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
        recipes: list[RecipeItem],
    ):
        self.event_manager.on(
            InventoryWeightEvent,
            partial(self.on_inventory_weight_event, recipes=recipes),
            originator=self,
            once=True,
        )
        req = ExchangeReadyRequest(ready=True, step=6)
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_inventory_weight_event(
        self, msg: InventoryWeightEvent, recipes: list[RecipeItem]
    ):
        self.event_manager.on(
            ExchangeLeaveEvent,
            partial(self.on_exchange_leave_event, recipes=recipes),
            originator=self,
            once=True,
        )
        self.run_timer(
            SMALL_RANGE, lambda: self.event_manager.send(DialogLeaveRequest())
        )

    def on_exchange_leave_event(
        self, msg: ExchangeLeaveEvent, recipes: list[RecipeItem]
    ):
        self.run_timer(SMALL_RANGE, lambda: self.process_recipe(recipes))
