from collections.abc import Iterable
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
from src.core.config import (
    BASE_RANGE,
    BOT_MINIMAL_KAMAS,
    MULE_BANK_CHARACTER_IDS,
    MULE_BANK_MAP_ID,
)


@dataclass
class MuleGiveBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior

    _step: int = field(init=False, default=0)
    _mule_bank_character_ids: Iterable[int] = field(
        init=False, default_factory=list[int]
    )

    def run(self) -> None:
        self._step = 0
        self._mule_bank_character_ids = MULE_BANK_CHARACTER_IDS
        if len(self._mule_bank_character_ids) == 0:
            self.logger.error("Mule bank character is not defined !")
            return self.finish()
        if self.game_state.inventory.pod_percentage >= 1:
            self.logger.info("Mule has too much pods to exchange")
            return self.finish()
        self.go_to_mule()

    def go_to_mule(self) -> None:
        self.auto_trip_smart_behavior.start(
            map_ids={MULE_BANK_MAP_ID},
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
        mule_id = next(
            (
                actor_id
                for actor_id in self.game_state.entity.actor_by_id
                if actor_id in self._mule_bank_character_ids
            ),
            None,
        )
        if mule_id is None:
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
