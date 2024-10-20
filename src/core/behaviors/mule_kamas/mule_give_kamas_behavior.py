from dataclasses import dataclass
from functools import partial

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeErrorEvent,
    ExchangeKamaModifiedEvent,
    ExchangeLeaveEvent,
    ExchangeMoveKamaRequest,
    ExchangePlayerRequest,
    ExchangeReadyRequest,
    ExchangeStartedWithPodsEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.config.suicide_bots import MULE_BANK_CHARACTER_ID, MULE_KAMAS_MAP_ID
from src.core.config.timings import BASE_RANGE


@dataclass
class MuleGiveKamasBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior

    def run(self, kamas: int) -> None:
        if kamas > self.game_state.inventory.kamas:
            self.logger.error("Bot doesn't have enough kamas !")
            return self.finish()
        if MULE_BANK_CHARACTER_ID is None:
            self.logger.error("Mule bank character is not defined !")
            return self.finish()
        self.auto_trip_smart_behavior.start(
            map_ids={MULE_KAMAS_MAP_ID},
            callback=partial(self.on_auto_trip_smart_behavior_finished, kamas=kamas),
            parent=self,
        )

    def on_auto_trip_smart_behavior_finished(self, error_code: str | None, kamas: int):
        self.event_manager.on(
            ExchangeStartedWithPodsEvent,
            partial(self.on_exchange_started_with_pods_event, kamas=kamas),
            originator=self,
            once=True,
        )
        self.event_manager.on(
            ExchangeErrorEvent, lambda _: self.finish(), originator=self, once=True
        )
        if MULE_BANK_CHARACTER_ID not in self.game_state.entity.actor_by_id:
            self.logger.warning("Mule bank not in map, skip giving kamas")
            return self.finish()
        req = ExchangePlayerRequest(target_id=MULE_BANK_CHARACTER_ID)
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))

    def on_exchange_started_with_pods_event(
        self, msg: ExchangeStartedWithPodsEvent, kamas: int
    ):
        self.event_manager.on(
            ExchangeKamaModifiedEvent,
            self.on_exchange_kama_modified_event,
            originator=self,
            once=True,
        )
        req = ExchangeMoveKamaRequest(quantity=kamas)
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))

    def on_exchange_kama_modified_event(self, msg: ExchangeKamaModifiedEvent):
        self.event_manager.on(
            ExchangeLeaveEvent, lambda _: self.finish(), originator=self, once=True
        )
        req = ExchangeReadyRequest(ready=True, step=1)
        self.run_timer((3, 4), lambda: self.event_manager.send(req))
