from dataclasses import dataclass
from functools import partial

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidBuyerStartedEvent,
)
from enums.element_type import ElementTypeEnum

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.config.timings import BASE_RANGE
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.models.npc_info import NpcInfo

BONTA_SALE_HOTEL_SELL_ACTION = NpcInfo(npc_id=-1, npc_action_id=5, npc_map_id=212601350)
ASTRUB_SALE_HOTEL_SELL_ACTION = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=191104004
)


@dataclass
class EnterSaleHotelBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    interactive_behavior: InteractiveBehavior

    def run(self) -> None:
        npc_info = (
            BONTA_SALE_HOTEL_SELL_ACTION
            if self.game_state.player.is_sub
            else ASTRUB_SALE_HOTEL_SELL_ACTION
        )
        self.auto_trip_smart_behavior.start(
            map_ids={npc_info.npc_map_id},
            callback=partial(self.on_auto_trip_smart_behavior, npc_info=npc_info),
            parent=self,
        )

    def on_auto_trip_smart_behavior(self, error_code: str | None, npc_info: NpcInfo):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        sale_hotel_interactive = next(
            interactive
            for interactive in self.game_state.interactive.interactive_element_by_id.values()
            if interactive.element_type_id == ElementTypeEnum.RESOURCE_SALE_HOTEL
        )
        self.event_manager.on(
            ExchangeBidBuyerStartedEvent,
            lambda msg: self.finish(npc_info=npc_info, bid_buyer_msg=msg),
            originator=self,
            once=True,
        )

        self.run_timer(
            BASE_RANGE,
            lambda: self.interactive_behavior.start(
                move_path=None,
                element_id=sale_hotel_interactive.element_id,
                skill_instance_uid=sale_hotel_interactive.enabled_skills[
                    0
                ].skill_instance_uid,
                callback=None,
                parent=self,
            ),
        )
