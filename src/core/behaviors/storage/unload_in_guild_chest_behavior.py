from dataclasses import dataclass, field
from functools import partial

from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
    ExchangeLeaveEvent,
)
from d3_mapping.resources.protos.game.guild_chest_pb2 import (
    GuildChestTabSelectRequest,
    GuildChestCurrentListenersAddEvent,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.const import BASE_RANGE, SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
    EnterGuildChestError,
)
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException


@dataclass
class UnloadInGuildChestBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    auto_trip_world_behavior: AutoTripSmartBehavior
    enter_guild_chest_behavior: EnterGuildChestBehavior

    object_to_unload_on_tab: list[tuple[int, list[ObjectItemInventory]]] = field(
        init=False, default_factory=list
    )

    def run(self, unload_item_id_by_tab: dict[int, set[int]]):
        object_by_gid_in_inventory = {
            object.item.gid: object
            for object in self.game_state.inventory.objects_by_uid.values()
        }
        self.object_to_unload_on_tab = [
            (tab, object_to_unloads)
            for tab, gids in unload_item_id_by_tab.items()
            if len(
                object_to_unloads := [
                    object
                    for gid in gids
                    if (object := object_by_gid_in_inventory.get(gid))
                ]
            )
            > 0
        ]
        if len(self.object_to_unload_on_tab) == 0:
            return self.finish()

        self.enter_guild_chest_behavior.start(
            callback=self.on_enter_guild_chest_behavior_finished, parent=self
        )

    def on_enter_guild_chest_behavior_finished(self, error_code: str | None):
        if error_code is EnterGuildChestError.DOES_NOT_RESPECT_CONDITION:
            return self.finish()
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.run_timer(BASE_RANGE, self.unload_tab)

    def unload_tab(self):
        if len(self.object_to_unload_on_tab) == 0:
            return self.run_timer(BASE_RANGE, self.on_all_unloaded)
        tab, object_to_unloads = self.object_to_unload_on_tab.pop()
        if tab != self.game_state.guild_chest.tab_number:
            self.event_manager.on(
                GuildChestCurrentListenersAddEvent,
                partial(
                    self.on_guild_chest_current_listeners_add_event,
                    object_to_unloads=object_to_unloads,
                ),
                once=True,
                originator=self,
            )
            return self.run_timer(
                SMALL_RANGE,
                lambda: self.event_manager.send(
                    GuildChestTabSelectRequest(tab_number=tab)
                ),
            )
        self.unload_object(object_to_unloads)

    def on_guild_chest_current_listeners_add_event(
        self,
        msg: GuildChestCurrentListenersAddEvent,
        object_to_unloads: list[ObjectItemInventory],
    ):
        self.unload_object(object_to_unloads)

    def unload_object(self, object_to_unloads: list[ObjectItemInventory]):
        self.logger.info(f"Unloading objects : {object_to_unloads}")
        if len(object_to_unloads) == 0:
            return self.run_timer(BASE_RANGE, self.unload_tab)

        self.event_manager.on(
            InventoryWeightEvent,
            partial(
                self.on_inventory_weight_event, object_to_unloads=object_to_unloads
            ),
            originator=self,
            once=True,
        )
        next_object = object_to_unloads.pop()
        req = ExchangeObjectMoveRequest(
            object_uid=next_object.item.uid, quantity=next_object.item.quantity
        )
        self.event_manager.send(req)

    def on_inventory_weight_event(
        self, msg: InventoryWeightEvent, object_to_unloads: list[ObjectItemInventory]
    ):
        self.run_timer(SMALL_RANGE, lambda: self.unload_object(object_to_unloads))

    def on_all_unloaded(self):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=lambda _: self.finish(),
            originator=self,
            once=True,
        )
        self.leave_all_dialogs()

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
        self.event_manager.send(request)
