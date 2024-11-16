from dataclasses import dataclass
from functools import partial

from D3Database.data_center.data_reader import DataReader
from D3Database.enums.category_item_enum import CategoryEnum
from D3Database.enums.element_type import ElementTypeEnum
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.config import BASE_RANGE
from src.core.engine.movements.map.map_tools import MapTools
from src.core.engine.movements.world.map_position import get_dist_to_maps
from src.core.engine.npcs.npc_info import NpcInfo
from src.core.game_constants import SALE_HOTELS_BY_CATEGORY
from src.exceptions import UnhandledErrorCodeException


@dataclass
class EnterSaleHotelBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    interactive_behavior: InteractiveBehavior

    def run(self, category: CategoryEnum) -> None:
        curr_map_pos = DataReader().map_pos_by_map_id[self.game_state.map.map_id]
        near_acessible_sale_hotel = min(
            [
                npc_info
                for npc_info in SALE_HOTELS_BY_CATEGORY[category]
                if self.game_state.player.is_sub
                != MapTools.is_map_allowed_for_unsub(npc_info.npc_map_id)
            ],
            key=lambda npc_info: get_dist_to_maps(
                curr_map_pos, [DataReader().map_pos_by_map_id[npc_info.npc_map_id]]
            ),
        )
        self.auto_trip_smart_behavior.start(
            map_ids={near_acessible_sale_hotel.npc_map_id},
            callback=partial(
                self.on_auto_trip_smart_behavior, npc_info=near_acessible_sale_hotel
            ),
            parent=self,
        )

    def on_auto_trip_smart_behavior(self, error_code: str | None, npc_info: NpcInfo):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        sale_hotel_interactive = next(
            interactive
            for interactive in self.game_state.interactive.interactive_element_by_id.values()
            if interactive.element_type_id
            in [
                ElementTypeEnum.RESOURCE_SALE_HOTEL,
                ElementTypeEnum.CONSUMABLE_SALE_HOTEL,
            ]
        )
        self.run_timer(
            BASE_RANGE,
            lambda: self.interactive_behavior.start(
                move_path=None,
                element_id=sale_hotel_interactive.element_id,
                skill_instance_uid=sale_hotel_interactive.enabled_skills[
                    0
                ].skill_instance_uid,
                callback=lambda _: self.finish(npc_info=npc_info),
                parent=self,
            ),
        )
