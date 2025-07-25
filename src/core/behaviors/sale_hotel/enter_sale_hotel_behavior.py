from dataclasses import dataclass
from functools import partial

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.map_reader import MapReader
from dofus_unity_reader.game_constants.element_type import ElementTypeEnum
from dofus_unity_reader.game_constants.item import CategoryItemEnum
from dofus_unity_reader.game_constants.npc import NpcInfo
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.config import BASE_RANGE
from src.core.engine.movements.map.map_tools import MapTools
from src.core.engine.movements.world.map_position import get_dist_to_maps
from src.core.frames.sale_hotel_frame import SALE_HOTELS_BY_CATEGORY


@dataclass
class EnterSaleHotelBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    interactive_behavior: InteractiveBehavior

    def run(self, category: CategoryItemEnum) -> None:
        curr_map_pos = DataReader().map_info_by_map_id[self.game_state.map.map_id]
        near_acessible_sale_hotel = min(
            [
                npc_info
                for npc_info in SALE_HOTELS_BY_CATEGORY[category]
                if self.game_state.player.is_sub
                != MapTools.is_map_allowed_for_unsub(npc_info.npc_map_id)
            ],
            key=lambda npc_info: get_dist_to_maps(
                curr_map_pos, [DataReader().map_info_by_map_id[npc_info.npc_map_id]]
            ),
        )
        self.auto_trip_smart_behavior.start(
            map_ids={near_acessible_sale_hotel.npc_map_id},
            callback=partial(
                self.on_auto_trip_smart_behavior, npc_info=near_acessible_sale_hotel
            ),
            parent=self,
        )

    def on_auto_trip_smart_behavior(
        self, error_code: str | None, npc_info: NpcInfo
    ) -> None:
        self.raise_if_error(error_code)
        sale_hotel_interactive = next(
            interactive
            for interactive in self.game_state.interactive.interactive_element_by_id.values()
            if interactive.element_type_id
            in [
                ElementTypeEnum.RESOURCE_SALE_HOTEL,
                ElementTypeEnum.CONSUMABLE_SALE_HOTEL,
                ElementTypeEnum.EQUIPMENT_SALE_HOTEL,
            ]
        )

        ref_data = MapReader().get_ref_data_by_element_id_by_map_id(self.game_state.map.map_id)[
            sale_hotel_interactive.element_id
        ]
        if ref_data.cellId is None:
            raise ValueError("Sale hotel cell id is missing")
        element_mp = MapPoint.from_cell_id(ref_data.cellId)

        def on_interactive_finished(_error_code: str | None) -> None:
            self.finish(npc_info=npc_info)

        self.run_timer(
            BASE_RANGE,
            lambda: self.interactive_behavior.start(
                element_mp=element_mp,
                element_id=sale_hotel_interactive.element_id,
                callback=on_interactive_finished,
                parent=self,
            ),
        )
