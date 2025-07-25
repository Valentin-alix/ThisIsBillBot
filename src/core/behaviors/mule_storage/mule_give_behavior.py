from dataclasses import dataclass, field

from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from datas.protos.non_obf.game.exchange_pb2 import (
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
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.bot.kamas_mule_registry import (
    KamasMuleRegistry,
    MuleReservation,
)
from src.core.config import (
    BASE_RANGE,
    BOT_MINIMAL_KAMAS,
)

@dataclass
class MuleGiveBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    mule_registry: KamasMuleRegistry = field(default_factory=KamasMuleRegistry)

    _step: int = field(init=False, default=0)
    _reservation: MuleReservation | None = field(init=False, default=None)

    def run(self) -> None:
        self._step = 0
        if self.game_state.inventory.pod_percentage >= 1:
            self.logger.info("Mule has too much pods to exchange")
            return self.finish()
        self._reservation = self.mule_registry.reserve(
            self.game_state.player.server_id,
            self.game_state.player.character_id,
        )
        if self._reservation is None:
            self.logger.info("No kamas mule is currently available")
            return self.finish()
        self.go_to_mule()

    def go_to_mule(self) -> None:
        assert self._reservation is not None
        self.auto_trip_smart_behavior.start(
            map_ids={self._reservation.map_id},
            callback=self.on_auto_trip_smart_behavior_finished,
            parent=self,
        )

    def on_auto_trip_smart_behavior_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            if error_code is MapChangeError.UNEXPECTED_NEW_MAP:
                return self.run_timer((2, 4), self.go_to_mule)
            self.raise_if_error(error_code)
        self.start_exchange_with_mule()

    def start_exchange_with_mule(self) -> None:
        assert self._reservation is not None
        if not self.mule_registry.is_reserved_by(
            self._reservation.mule_login,
            self.game_state.player.character_id,
        ):
            self.logger.info("Kamas mule reservation expired before exchange")
            return self.finish()
        mule_id = self._reservation.mule_character_id
        if mule_id not in self.game_state.entity.actor_by_id:
            self.logger.warning("Mule bank not in map")
            return self.finish()

        self.event_manager.on(
            ExchangeStartedWithPodsEvent,
            self.on_exchange_started_with_pods_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.event_manager.on(
            ExchangeErrorEvent,
            lambda _: self.finish(),
            originator=self,
            once=True,
            override_on_self=True,
        )
        req = ExchangePlayerRequest(target_id=mule_id)
        self.send_message_delayed(req, BASE_RANGE)

    def on_exchange_started_with_pods_event(
        self, msg: ExchangeStartedWithPodsEvent
    ) -> None:
        self._step = 0
        return self.depose_kamas_in_exchange()

    def depose_kamas_in_exchange(self) -> None:
        kamas_to_gives = self.game_state.inventory.kamas - BOT_MINIMAL_KAMAS
        if kamas_to_gives <= 0:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.finish(),
                originator=self,
            )
            req = DialogLeaveRequest()
            return self.send_message_delayed(req, BASE_RANGE)
        self.event_manager.on(
            ExchangeKamaModifiedEvent,
            lambda _: self.accept_exchange(),
            originator=self,
            once=True,
            override_on_self=True,
        )
        self._step += 1
        move_kama_req = ExchangeMoveKamaRequest(quantity=kamas_to_gives)
        self.send_message_delayed(move_kama_req, BASE_RANGE)

    def accept_exchange(self) -> None:
        self.event_manager.on(
            ExchangeLeaveEvent,
            lambda _: self.finish(),
            originator=self,
            once=True,
            override_on_self=True,
        )
        req = ExchangeReadyRequest(ready=True, step=self._step)
        self.send_message_delayed(req, (3, 4))

    def clear_behavior(self) -> None:
        if self._reservation is not None:
            self.mule_registry.release(self._reservation.token)
            self._reservation = None
        super().clear_behavior()
