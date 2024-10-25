from dataclasses import dataclass

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeAcceptRequest,
    ExchangeReadyEvent,
    ExchangeReadyRequest,
    ExchangeRequestedTradeEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.config.mule_kamas import MULE_KAMAS_MAP_ID
from src.core.config.timings import BASE_RANGE


@dataclass
class MuleAcceptKamasBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior

    def run(self) -> None:
        self.auto_trip_smart_behavior.start(
            map_ids={MULE_KAMAS_MAP_ID},
            parent=self,
            callback=self.on_auto_trip_smart_behavior_finished,
        )

    def on_auto_trip_smart_behavior_finished(self, error_code: str | None):
        self.event_manager.on(
            ExchangeRequestedTradeEvent,
            self.on_exchange_requested_trade_event,
            originator=self,
        )

    def on_exchange_requested_trade_event(self, msg: ExchangeRequestedTradeEvent):
        if msg.target_id != self.game_state.player.character_id:
            return
        self.event_manager.clear_listener_by_origin_and_type(ExchangeReadyEvent, self)
        self.event_manager.on(
            ExchangeReadyEvent, self.on_exchange_ready_event, originator=self, once=True
        )
        self.run_timer(
            BASE_RANGE, lambda: self.event_manager.send(ExchangeAcceptRequest())
        )

    def on_exchange_ready_event(self, msg: ExchangeReadyEvent):
        if not msg.ready:
            return
        self.run_timer(
            BASE_RANGE,
            lambda: self.event_manager.send(ExchangeReadyRequest(ready=True, step=1)),
        )
