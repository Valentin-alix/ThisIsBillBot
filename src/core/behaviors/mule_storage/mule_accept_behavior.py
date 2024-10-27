from dataclasses import dataclass, field
from datetime import datetime, timedelta

from d3_mapping.resources.protos.game.dialog_pb2 import (
    DialogLeaveRequest,
)
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeAcceptRequest,
    ExchangeKamaModifiedEvent,
    ExchangeLeaveEvent,
    ExchangeObjectsAddedEvent,
    ExchangeReadyEvent,
    ExchangeReadyRequest,
    ExchangeRequestedTradeEvent,
    ExchangeStartedWithPodsEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.consts import USEFUL_UNLOAD
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config.mule import MULE_BANK_CHARACTER_IDS, MULE_BANK_MAP_ID
from src.core.config.timings import (
    BASE_RANGE,
    get_time_beween_sale_hotel_prices,
)
from src.exceptions import UnhandledErrorCodeException


@dataclass
class MuleAcceptBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    unload_behavior: UnloadBehavior
    sale_hotel_prices_behavior: SaleHotelPricesBehavior

    _timedelta_for_sale_hotel_prices: timedelta = field(
        init=False, default_factory=get_time_beween_sale_hotel_prices
    )
    _step: int = field(init=False, default=0)

    def run(self) -> None:
        # TODO Comment gérer les déco du client ? fake un movement ?
        MULE_BANK_CHARACTER_IDS.add(self.game_state.player.character_id)
        self.go_bank_map()

    def go_bank_map(self):
        self.auto_trip_smart_behavior.start(
            map_ids={MULE_BANK_MAP_ID},
            parent=self,
            callback=lambda _: self.on_bank_map(),
        )

    def on_bank_map(self):
        if (
            datetime.now() - self.game_state.sale_hotel.last_time_updated_prices
            > self._timedelta_for_sale_hotel_prices
        ):
            self._timedelta_for_sale_hotel_prices = get_time_beween_sale_hotel_prices()
            return self.sale_hotel_prices_behavior.start(
                callback=self.on_sale_hotel_price_behavior_finished, parent=self
            )

        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            self.unload_behavior.start(
                callback=lambda _: self.stand_ready_for_exchanges(), parent=self
            )
        else:
            self.stand_ready_for_exchanges()

    def on_sale_hotel_price_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.go_bank_map()

    def stand_ready_for_exchanges(self):
        self.event_manager.on(
            ExchangeRequestedTradeEvent,
            self.on_exchange_requested_trade_event,
            originator=self,
            once=True,
            override_on_self=True,
        )

    def on_exchange_requested_trade_event(self, msg: ExchangeRequestedTradeEvent):
        self.logger.info("on requested trade event, let's accept")
        self.event_manager.on(
            ExchangeStartedWithPodsEvent,
            callback=self.on_exchange_started_with_pods_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.run_timer(
            BASE_RANGE, lambda: self.event_manager.send(ExchangeAcceptRequest())
        )

    def on_exchange_started_with_pods_event(self, msg: ExchangeStartedWithPodsEvent):
        self.event_manager.on(
            ExchangeLeaveEvent,
            self.on_exchange_leave_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.event_manager.on(
            ExchangeReadyEvent,
            self.on_exchange_ready_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.event_manager.on(
            ExchangeObjectsAddedEvent,
            lambda _: self.increment_step(),
            originator=self,
            override_on_self=True,
        )
        self.event_manager.on(
            ExchangeKamaModifiedEvent,
            lambda _: self.increment_step(),
            originator=self,
            override_on_self=True,
        )
        self._step = 0

    def increment_step(self):
        self._step += 1

    def on_exchange_ready_event(self, msg: ExchangeReadyEvent):
        self.event_manager.on(
            ExchangeRequestedTradeEvent,
            self.on_exchange_requested_trade_event_during_unload,
            originator=self,
            override_on_self=True,
        )
        self.run_timer(
            BASE_RANGE,
            lambda: self.event_manager.send(
                ExchangeReadyRequest(ready=True, step=self._step)
            ),
        )

    def on_exchange_requested_trade_event_during_unload(
        self, msg: ExchangeRequestedTradeEvent
    ):
        self.logger.info("Canceling request bc we are unloading")
        # auto cancel exchange request
        req = DialogLeaveRequest()
        self.event_manager.send(req)

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent):
        self.run_timer(BASE_RANGE, self.on_bank_map)
