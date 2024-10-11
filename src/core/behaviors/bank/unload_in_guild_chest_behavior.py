from dataclasses import dataclass, field

from protos.game.common_pb2 import ObjectItemInventory
from protos.game.dialog_pb2 import DialogLeaveRequest
from protos.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
    ExchangeLeaveEvent,
)
from protos.game.guild_chest_pb2 import GuildChestCurrentListenersAddEvent
from protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.const import BASE_RANGE, SMALL_RANGE
from src.core.behaviors.bank.consts import BANK_MAP_IDS
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.data_center.map_reader import MapReader
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.element_type import ElementTypeEnum
from src.interfaces.enums.guild_rank_enum import GuildRankEnum


@dataclass
class UnloadInGuildChestBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    auto_trip_world_behavior: AutoTripSmartBehavior

    object_to_unload: list[ObjectItemInventory] = field(
        init=False, default_factory=list
    )

    def run(self, unload_item_ids: set[int]):
        if (
            not self.game_state.player.is_sub
            or self.game_state.player.guild_rank_id
            not in [GuildRankEnum.LEADER, GuildRankEnum.OFFICER]
        ):
            return self.finish()

        self.object_to_unload = [
            object
            for object in self.game_state.inventory.objects_by_uid.values()
            if object.item.gid in unload_item_ids
        ]
        if len(self.object_to_unload) == 0:
            return self.finish()

        self.auto_trip_world_behavior.start(
            callback=self.on_bank_map,
            parent=self,
            map_ids={bank_map_id for bank_map_id in BANK_MAP_IDS},
        )

    def on_bank_map(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        chest_interactive = next(
            element
            for element in self.game_state.interactive.interactive_element_by_id.values()
            if element.element_type_id == ElementTypeEnum.GUILD_CHEST
        )
        ref_data = MapReader().get_ref_data_by_element_id(self.game_state.map.map_id)[
            chest_interactive.element_id
        ]

        move_path_to_chest = self.path_finding.find_path(
            self.game_state.player.map_point, {MapPoint.from_cell_id(ref_data.cellId)}
        )

        self.interactive_behavior.start(
            move_path=move_path_to_chest,
            element_id=chest_interactive.element_id,
            skill_instance_uid=chest_interactive.enabled_skills[0].skill_instance_uid,
            callback=self.on_interactive_behavior_finished,
            parent=self,
        )

    def on_interactive_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            self.on_guild_chest_current_listeners_add_event,
            originator=self,
        )

    def on_guild_chest_current_listeners_add_event(
        self, msg: GuildChestCurrentListenersAddEvent
    ):
        self.run_timer(BASE_RANGE, self.unload_object)

    def unload_object(self):
        self.logger.info(f"Unloading objects : {self.object_to_unload}")
        if len(self.object_to_unload) == 0:
            return self.run_timer(BASE_RANGE, self.on_all_unloaded)

        self.event_manager.on(
            InventoryWeightEvent,
            self.on_inventory_weight_event,
            originator=self,
            once=True,
        )
        next_object = self.object_to_unload.pop()
        req = ExchangeObjectMoveRequest(
            object_uid=next_object.item.uid, quantity=next_object.item.quantity
        )
        self.event_manager.send(req)

    def on_inventory_weight_event(self, msg: InventoryWeightEvent):
        self.run_timer(SMALL_RANGE, self.unload_object)

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
