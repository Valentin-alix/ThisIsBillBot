from dataclasses import dataclass, field
from functools import partial

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
)
from datas.protos.non_obf.game.guild_chest_pb2 import (
    GuildChestTabSelectRequest,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
    StorageInventoryContentEvent,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.item import ItemTypeEnum

from src.core.behaviors.recovery import RecoverableBehavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.services.human_timings import HumanTimingsService
from src.core.engine.items.item import is_exchangeable_item
from src.core.engine.items.item_formatter import format_item_name
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from dofus_unity_reader.game_constants.guild import UNBOUNDED_CHEST_TAB_NUMBER


@dataclass
class UnloadInGuildChestBehavior(RecoverableBehavior):
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    auto_trip_world_behavior: AutoTripSmartBehavior
    enter_guild_chest_behavior: EnterGuildChestBehavior

    object_to_unload_on_tab: list[tuple[int, list[ObjectItemInventory]]] = field(
        init=False, default_factory=list[tuple[int, list[ObjectItemInventory]]]
    )

    def run(self, unload_item_id_by_tab: dict[int, set[int]]) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(
            lambda: self.start_guild_chest_unload(unload_item_id_by_tab=unload_item_id_by_tab)
        )

    def start_guild_chest_unload(self, unload_item_id_by_tab: dict[int, set[int]]) -> None:
        object_by_gid_in_inventory = {
            object.item.gid: object for object in self.game_state.inventory.objects_by_uid.values()
        }
        self.logger.info(f"Inventory contains {len(object_by_gid_in_inventory)} unique items")

        self.object_to_unload_on_tab = []
        gids_treaded: set[int] = set()
        for tab, gids in unload_item_id_by_tab.items():
            object_to_unloads: list[ObjectItemInventory] = []
            for gid in gids:
                if (
                    (object := object_by_gid_in_inventory.get(gid))
                    and gid not in gids_treaded
                    and is_exchangeable_item(DataReader().item_by_id[gid])
                    and DataReader().item_by_id[gid].typeId != ItemTypeEnum.REKLOOT
                ):
                    gids_treaded.add(gid)
                    object_to_unloads.append(object)
            if len(object_to_unloads) > 0:
                self.object_to_unload_on_tab.append((tab, object_to_unloads))

        total_items = sum(len(objects) for _, objects in self.object_to_unload_on_tab)
        tabs_summary = ", ".join(
            [f"Tab {tab}: {len(objects)} items" for tab, objects in self.object_to_unload_on_tab]
        )
        self.logger.info(
            f"Will unload {total_items} items across {len(self.object_to_unload_on_tab)} tabs ({tabs_summary})"
        )

        if len(self.object_to_unload_on_tab) == 0:
            return self.finish()

        self.enter_guild_chest_behavior.start(
            callback=self.on_enter_guild_chest_behavior_finished, parent=self
        )

    def on_enter_guild_chest_behavior_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            return self.finish(error_code)

        available_tabs = set(self.game_state.guild_chest.tabs)
        filtered = [(tab, objects) for tab, objects in self.object_to_unload_on_tab if tab in available_tabs]
        filtered_out_count = len(self.object_to_unload_on_tab) - len(filtered)
        self.object_to_unload_on_tab = filtered

        if filtered_out_count > 0:
            self.logger.warning(f"Filtered out {filtered_out_count} tabs (not accessible)")
        self.logger.info(f"Starting unload process for {len(self.object_to_unload_on_tab)} accessible tabs")
        self.run_timer(HumanTimingsService().get_timing_base_action(), self.unload_tab)

    def unload_tab(self) -> None:
        if len(self.object_to_unload_on_tab) == 0:
            return self.run_timer(HumanTimingsService().get_timing_base_action(), self.on_all_unloaded)
        tab, object_to_unloads = self.object_to_unload_on_tab.pop()
        if tab != self.game_state.guild_chest.tab_number:
            self.event_manager.on(
                StorageInventoryContentEvent,
                partial(
                    self.on_storage_inventory_content_event,
                    object_to_unloads=object_to_unloads,
                ),
                once=True,
                originator=self,
                override_on_self=True,
            )
            return self.run_timer(
                HumanTimingsService().get_timing_short_action(),
                lambda: self.event_manager.send(GuildChestTabSelectRequest(tab_number=tab)),
            )
        self.unload_object(object_to_unloads)

    def on_storage_inventory_content_event(
        self,
        msg: StorageInventoryContentEvent,
        object_to_unloads: list[ObjectItemInventory],
    ) -> None:
        self.run_timer(
            HumanTimingsService().get_timing_short_action(), lambda: self.unload_object(object_to_unloads)
        )

    def unload_object(self, object_to_unloads: list[ObjectItemInventory]) -> None:
        if len(object_to_unloads) == 0:
            self.logger.info("Finished unloading current tab")
            return self.run_timer(HumanTimingsService().get_timing_base_action(), self.unload_tab)

        self.event_manager.on(
            InventoryWeightEvent,
            partial(self.on_inventory_weight_event, object_to_unloads=object_to_unloads),
            originator=self,
            once=True,
            override_on_self=True,
        )
        next_object = object_to_unloads.pop()
        item_name = format_item_name(next_object.item.gid)

        storage = self.game_state.guild_chest.storage
        tab_size = storage.get_tab_size(self.game_state.guild_chest.tab_number)
        item_in_chest = storage.get_item_by_gid(
            self.game_state.guild_chest.tab_number,
            next_object.item.gid,
        )

        if item_in_chest is None and tab_size == UNBOUNDED_CHEST_TAB_NUMBER:
            self.logger.warning(
                f"Tab {self.game_state.guild_chest.tab_number} is full (100/100 slots), skipping {item_name}"
            )
            return self.run_timer(
                HumanTimingsService().get_timing_short_action(), lambda: self.unload_object(object_to_unloads)
            )

        self.logger.info(
            f"Unloading {item_name} x{next_object.item.quantity} ({len(object_to_unloads)} remaining)"
        )
        req = ExchangeObjectMoveRequest(object_uid=next_object.item.uid, quantity=next_object.item.quantity)
        self.event_manager.send(req)

    def on_inventory_weight_event(
        self, msg: InventoryWeightEvent, object_to_unloads: list[ObjectItemInventory]
    ) -> None:
        self.run_timer(
            HumanTimingsService().get_timing_short_action(), lambda: self.unload_object(object_to_unloads)
        )

    def on_all_unloaded(self) -> None:
        self.logger.info("Guild chest unload completed")
        self.finish()
