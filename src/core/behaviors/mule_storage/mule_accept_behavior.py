from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Timer
import time

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

from scraping_d3_client.scraping_d3_client.models.character_action_enum import (
    CharacterActionEnum,
)
from src.controller.scraping_d3 import ScrapingD3Controller
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_scraping_behavior import (
    SaleHotelScrapingBehavior,
)
from src.core.config.storage import USEFUL_UNLOAD
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config.mule import MULE_BANK_MAP_ID
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
    sale_hotel_scraping_behavior: SaleHotelScrapingBehavior

    _timedelta_for_sale_hotel_prices: timedelta = field(
        init=False, default_factory=get_time_beween_sale_hotel_prices
    )
    _step: int = field(init=False, default=0)
    _time_since_activity: float = field(init=False, default_factory=time.perf_counter)
    _timer_go_scraping: Timer | None = field(init=False, default=None)

    def run(self) -> None:
        ScrapingD3Controller.patch_character_action(
            self.game_state.player.character_id, CharacterActionEnum.MULE_ACCEPT_BANK
        )
        self.go_bank_map()

    def stop(self) -> None:
        ScrapingD3Controller.patch_character_action(
            self.game_state.player.character_id, None
        )
        return super().stop()

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
        self._time_since_activity = time.perf_counter()
        self._timer_go_scraping = Timer(60 * 14, self.on_inactivity_go_scraping)
        self._timer_go_scraping.start()
        self.event_manager.on(
            ExchangeRequestedTradeEvent,
            self.on_exchange_requested_trade_event,
            originator=self,
            once=True,
            override_on_self=True,
        )

    def on_inactivity_go_scraping(self):
        self.event_manager.clear_listener_by_origin_and_type(
            ExchangeRequestedTradeEvent, self
        )
        self.sale_hotel_scraping_behavior.start(
            callback=lambda _: self.go_bank_map(), parent=self
        )

    def on_exchange_requested_trade_event(self, msg: ExchangeRequestedTradeEvent):
        if self._timer_go_scraping:
            self._timer_go_scraping.cancel()
            self._timer_go_scraping = None

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
