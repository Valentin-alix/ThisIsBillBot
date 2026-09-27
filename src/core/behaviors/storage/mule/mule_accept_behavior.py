from dataclasses import dataclass, field

from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import (
    PlayerStatusUpdatedEvent,
    PlayerStatusUpdateRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import CharacterStatus
from DBDofusUnity.datas.protos.non_obf.game.dialog_pb2 import (
    DialogLeaveRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeAcceptRequest,
    ExchangeKamaModifiedEvent,
    ExchangeLeaveEvent,
    ExchangeObjectsAddedEvent,
    ExchangeReadyEvent,
    ExchangeReadyRequest,
    ExchangeRequestedTradeEvent,
    ExchangeStartedWithPodsEvent,
)
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.recovery_behavior import RecoverableBehavior
from src.core.behaviors.sale_hotel.sale_hotel_sell_behavior import (
    SaleHotelSellBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.bot.kamas_mule_registry import KamasMuleRegistry
from src.core.config import (
    MULE_BANK_MAP_ID,
    USEFUL_UNLOAD,
)
from src.services.human_timings import HumanTimingsService


@dataclass
class MuleAcceptBehavior(RecoverableBehavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    unload_behavior: UnloadBehavior
    sale_hotel_prices_behavior: SaleHotelSellBehavior
    mule_registry: KamasMuleRegistry = field(default_factory=KamasMuleRegistry)

    _step: int = field(init=False, default=0)
    _exchange_token: str | None = field(init=False, default=None)
    _coordination_connected: bool = field(init=False, default=False)

    def run(self) -> None:
        signals = self.mule_registry.exchange_signals
        signals.connect_direct(signals.preparation_requested, self.prepare_exchange)
        signals.connect_direct(signals.cancelled, self.cancel_exchange_preparation)
        self._coordination_connected = True
        self.init_recovery_listeners()
        self.ensure_free_to_act(self.start_accepting)

    def start_accepting(self) -> None:
        self._step = 0
        self.go_bank_map()

    def go_bank_map(self) -> None:
        def on_bank_map_reached(error_code: str | None) -> None:
            self.raise_if_error(error_code)
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

            def on_unload_finished(error_code: str | None) -> None:
                self.raise_if_error(error_code)
                self.stand_ready_for_exchanges()

            self.unload_behavior.start(callback=on_unload_finished, parent=self)
        else:
            self.stand_ready_for_exchanges()

    def on_sale_hotel_price_behavior_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self.go_bank_map()

    def stand_ready_for_exchanges(self) -> None:
        self.listen_for_exchange_request()
        self.mule_registry.mark_ready(
            self.game_state.player.login,
            self.game_state.player.server_id,
            self.game_state.player.character_id,
            self.game_state.map.map_id,
        )

    def prepare_exchange(self, token: str) -> None:
        if not self.mule_registry.is_reserved_for(token, self.game_state.player.login):
            return
        if self._exchange_token == token:
            return
        self._exchange_token = token
        self.event_manager.on(
            PlayerStatusUpdatedEvent,
            self.on_player_status_updated,
            originator=self,
            override_on_self=True,
        )
        self.event_manager.send(
            PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_AVAILABLE))
        )

    def on_player_status_updated(self, msg: PlayerStatusUpdatedEvent) -> None:
        if (
            msg.player_id != self.game_state.player.character_id
            or msg.status.status != CharacterStatus.STATUS_AVAILABLE
        ):
            return
        self.unregister_listener(PlayerStatusUpdatedEvent)
        token = self._exchange_token
        if token is not None and self.mule_registry.is_reserved_for(token, self.game_state.player.login):
            self.mule_registry.exchange_signals.prepared.emit(token)

    def cancel_exchange_preparation(self, token: str) -> None:
        if token == self._exchange_token:
            self.restore_solo()

    def listen_for_exchange_request(self) -> None:
        self.event_manager.on(
            ExchangeRequestedTradeEvent,
            self.on_exchange_requested_trade_event,
            originator=self,
            once=True,
            override_on_self=True,
        )

    def on_exchange_requested_trade_event(self, msg: ExchangeRequestedTradeEvent) -> None:
        if not self.mule_registry.is_reserved_by(self.game_state.player.login, msg.source_id):
            self.logger.info(f"Rejecting unreserved exchange request from {msg.source_id}")
            self.listen_for_exchange_request()
            self.event_manager.send(DialogLeaveRequest())
            return
        self.logger.info("on requested trade event, let's accept")
        self.event_manager.on(
            ExchangeStartedWithPodsEvent,
            callback=self.on_exchange_started_with_pods_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.send_message_delayed(ExchangeAcceptRequest(), HumanTimingsService().get_timing_base_action())

    def on_exchange_started_with_pods_event(self, msg: ExchangeStartedWithPodsEvent) -> None:
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
        req = ExchangeReadyRequest(ready=True, step=self._step)
        self.send_message_delayed(req, HumanTimingsService().get_timing_base_action())

    def on_exchange_requested_trade_event_during_unload(self, msg: ExchangeRequestedTradeEvent) -> None:
        self.logger.info("Canceling request bc we are unloading")

        req = DialogLeaveRequest()
        self.event_manager.send(req)

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent) -> None:
        self.stop_accepting_exchanges()
        self.run_timer(HumanTimingsService().get_timing_base_action(), self.on_bank_map)

    def stop_accepting_exchanges(self) -> None:
        self.mule_registry.mark_unavailable(self.game_state.player.login)
        self.unregister_listener(ExchangeRequestedTradeEvent)
        self.restore_solo()

    def restore_solo(self) -> None:
        token = self._exchange_token
        self._exchange_token = None
        self.unregister_listener(PlayerStatusUpdatedEvent)
        if token is not None and self.event_manager.on_send_game_callback is not None:
            self.event_manager.send(
                PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_SOLO))
            )

    def clear_behavior(self) -> None:
        self.stop_accepting_exchanges()
        if self._coordination_connected:
            self.mule_registry.exchange_signals.preparation_requested.disconnect(self.prepare_exchange)
            self.mule_registry.exchange_signals.cancelled.disconnect(self.cancel_exchange_preparation)
            self._coordination_connected = False
        super().clear_behavior()
