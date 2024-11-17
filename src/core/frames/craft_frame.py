from dataclasses import dataclass, field

from D3Database.data_center.data_reader import DataReader
from D3Database.models.datas.recipe_root import RecipeItem
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeCraftCountRequest,
    ExchangeCraftStartedEvent,
    ExchangeLeaveEvent,
    ExchangeReadyRequest,
    ExchangeSetCraftRecipeRequest,
)
from src.core.frames.frame import Frame


@dataclass
class CraftFrame(Frame):
    _current_recipe: RecipeItem | None = field(init=False, default=None)
    _requested_craft_count: int = field(init=False, default=1)

    def __post_init__(self):
        self.event_manager.on(
            ExchangeCraftStartedEvent,
            self.on_exchange_craft_started_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeLeaveEvent,
            self.on_exchange_leave_event,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_craft_started_event(self, _msg: ExchangeCraftStartedEvent):
        self.logger.info("Craft exchange started, listening for recipe selection")
        self.event_manager.on(
            ExchangeSetCraftRecipeRequest,
            self.on_exchange_set_craft_recipe_request,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_set_craft_recipe_request(self, msg: ExchangeSetCraftRecipeRequest):
        self._requested_craft_count = 1
        recipe_gid = msg.object_uid
        self._current_recipe = DataReader().recipe_by_result_id[recipe_gid]
        self.logger.info(
            f"Recipe selected: {self._current_recipe.resultId} with ingredients {self._current_recipe.ingredientIds}"
        )
        self.event_manager.on(
            ExchangeCraftCountRequest,
            self.on_exchange_craft_count_request,
            originator=self,
            priority=self.priority,
            override_on_self=True,
        )
        self.event_manager.on(
            ExchangeReadyRequest,
            self.on_exchange_ready_request,
            originator=self,
            priority=self.priority,
            override_on_self=True,
            once=True,
        )

    def on_exchange_craft_count_request(self, msg: ExchangeCraftCountRequest):
        self._requested_craft_count = msg.count
        self.logger.info(f"Craft count requested: {self._requested_craft_count}")

    def on_exchange_ready_request(self, msg: ExchangeReadyRequest):
        if not self._current_recipe or self._requested_craft_count == 0:
            self.logger.warning(
                "Inventory weight event on craft but no treating a recipe ?!"
            )
            return

        self.logger.info(
            f"Craft completed, removing {self._requested_craft_count}x ingredients for recipe {self._current_recipe.resultId}"
        )

        for ingredient_gid, quantity_per_craft in zip(
            self._current_recipe.ingredientIds, self._current_recipe.quantities
        ):
            total_quantity_consumed = quantity_per_craft * self._requested_craft_count

            inventory_item = self.game_state.inventory.get_object_item_by_gid(
                ingredient_gid
            )
            assert inventory_item
            new_quantity = inventory_item.item.quantity - total_quantity_consumed
            assert new_quantity >= 0
            self.logger.info(
                f"Ingredient {ingredient_gid}: {inventory_item.item.quantity} -> {new_quantity}"
            )
            if new_quantity == 0:
                self.game_state.inventory.remove_object(inventory_item.item.uid)
            else:
                inventory_item.item.quantity = new_quantity
                self.inventory_signals.updated_object_item.emit(inventory_item)

    def on_exchange_leave_event(self, _: ExchangeLeaveEvent):
        self.logger.info("Craft exchange ended, clearing listeners")
        self.unregister_listener(ExchangeSetCraftRecipeRequest)
        self.unregister_listener(ExchangeCraftCountRequest)
        self.unregister_listener(ExchangeReadyRequest)
