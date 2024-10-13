from dataclasses import dataclass

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidBuyerStartedEvent,
    ExchangeBidSellerStartedEvent,
)
from d3_mapping.resources.protos.game.npc_pb2 import NpcGenericActionRequest
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.element_type import ElementTypeEnum
from src.interfaces.models.npc_info import NpcGenericAction

BONTA_SALE_HOTEL_SELL_ACTION = NpcGenericAction(
    npc_id=-1, npc_action_id=5, npc_map_id=212601350
)


@dataclass
class EnterSaleHotelSellBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    interactive_behavior: InteractiveBehavior

    def run(self) -> None:
        self.auto_trip_smart_behavior.start(
            map_ids={BONTA_SALE_HOTEL_SELL_ACTION.npc_map_id},
            callback=self.on_auto_trip_smart_behavior,
            parent=self,
        )

    def on_auto_trip_smart_behavior(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        sale_hotel_interactive = next(
            interactive
            for interactive in self.game_state.interactive.interactive_element_by_id.values()
            if interactive.element_type_id == ElementTypeEnum.RESOURCE_SALE_HOTEL
        )
        self.event_manager.on(
            ExchangeBidBuyerStartedEvent,
            self.on_exchange_bid_buyer_started_event,
            originator=self,
            once=True,
        )
        self.interactive_behavior.start(
            move_path=None,
            element_id=sale_hotel_interactive.element_id,
            skill_instance_uid=sale_hotel_interactive.enabled_skills[
                0
            ].skill_instance_uid,
            callback=None,
            parent=self,
        )

    def on_exchange_bid_buyer_started_event(self, msg: ExchangeBidBuyerStartedEvent):
        self.event_manager.on(
            ExchangeBidSellerStartedEvent,
            self.on_exchange_bid_seller_started_event,
            originator=self,
            once=True,
        )
        req = NpcGenericActionRequest(
            npc_id=BONTA_SALE_HOTEL_SELL_ACTION.npc_id,
            npc_map_id=BONTA_SALE_HOTEL_SELL_ACTION.npc_map_id,
            npc_action_id=BONTA_SALE_HOTEL_SELL_ACTION.npc_action_id,
        )
        self.event_manager.send(req)

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent):
        self.finish(items=msg.items)
