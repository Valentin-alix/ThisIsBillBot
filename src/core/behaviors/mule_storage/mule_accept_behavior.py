from dataclasses import dataclass, field

from datas.protos.non_obf.game.dialog_pb2 import (
    DialogLeaveRequest,
)
from datas.protos.non_obf.game.exchange_pb2 import (
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
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import (
    BASE_RANGE,
    MULE_BANK_MAP_ID,
    USEFUL_UNLOAD,
)


@dataclass
class MuleAcceptBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    unload_behavior: UnloadBehavior
    sale_hotel_prices_behavior: SaleHotelPricesBehavior

    _step: int = field(init=False, default=0)

    def run(self) -> None:
        self.go_bank_map()

    def go_bank_map(self) -> None:
        def on_bank_map_reached(_error_code: str | None) -> None:
            self.on_bank_map()

        self.auto_trip_smart_behavior.start(
            map_ids={MULE_BANK_MAP_ID},
            parent=self,
            callback=on_bank_map_reached,
        )

    def on_bank_map(self) -> None:
        if self.game_state.sale_hotel.should_update_price:
            return self.sale_hotel_prices_behavior.start(
                callback=self.on_sale_hotel_price_behavior_finished, parent=self
            )

        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:

            def on_unload_finished(_error_code: str | None) -> None:
                self.stand_ready_for_exchanges()

            self.unload_behavior.start(callback=on_unload_finished, parent=self)
        else:
            self.stand_ready_for_exchanges()

    def on_sale_hotel_price_behavior_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self.go_bank_map()

    def stand_ready_for_exchanges(self) -> None:
        self.event_manager.on(
            ExchangeRequestedTradeEvent,
            self.on_exchange_requested_trade_event,
            originator=self,
            once=True,
            override_on_self=True,
        )

    def on_exchange_requested_trade_event(
        self, msg: ExchangeRequestedTradeEvent
    ) -> None:
        self.logger.info("on requested trade event, let's accept")
        self.event_manager.on(
            ExchangeStartedWithPodsEvent,
            callback=self.on_exchange_started_with_pods_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.send_message_delayed(ExchangeAcceptRequest(), BASE_RANGE)

    def on_exchange_started_with_pods_event(
        self, msg: ExchangeStartedWithPodsEvent
    ) -> None:
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
            lambda _msg: self.increment_step(),
            originator=self,
            override_on_self=True,
        )
        self.event_manager.on(
            ExchangeKamaModifiedEvent,
            lambda _msg: self.increment_step(),
            originator=self,
            override_on_self=True,
        )
        self._step = 0

    def increment_step(self) -> None:
        self._step += 1

    def on_exchange_ready_event(self, msg: ExchangeReadyEvent) -> None:
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
    ) -> None:
        self.logger.info("Canceling request bc we are unloading")
        # auto cancel exchange request
        req = DialogLeaveRequest()
        self.event_manager.send(req)

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent) -> None:
        self.run_timer(BASE_RANGE, self.on_bank_map)
