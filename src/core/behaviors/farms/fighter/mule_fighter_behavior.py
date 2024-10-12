from dataclasses import dataclass, field
from functools import partial

from protos.game.context_pb2 import ContextCreationEvent
from protos.game.multi_account_pb2 import (
    PartyInvitationEvent,
    PartyInvitationAcceptRequest,
    PartyJoinEvent,
    FightAutoJoinActivationRequest,
    FightAutoJoinActivationResponse,
)
from src.const import BASE_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripErrorCode
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.unload_behavior import UnloadBehavior
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.models.barrier import SubjectBarrier


@dataclass
class MuleFighterBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    fight_behavior: FightBehavior
    unload_behavior: UnloadBehavior

    ready_barrier: SubjectBarrier = field(init=False, default_factory=SubjectBarrier)

    def run(self, leader_id: int, ready_barrier: SubjectBarrier) -> None:
        self.ready_barrier = ready_barrier
        self.event_manager.on(
            PartyInvitationEvent,
            partial(self.on_party_invitation_event, target_leader_id=leader_id),
            originator=self,
        )

    def on_party_invitation_event(
        self, msg: PartyInvitationEvent, target_leader_id: int
    ):
        if (
            msg.to_player_id != self.game_state.player.character_id
            or msg.from_player_id != target_leader_id
        ):
            return self.logger.info(
                f"Got party invitation but {msg.to_player_id} !=  {self.game_state.player.character_id} or {msg.from_player_id} != {target_leader_id}"
            )

        self.event_manager.on(
            PartyJoinEvent,
            partial(self.on_party_join_event),
            originator=self,
        )

        req = PartyInvitationAcceptRequest(party_id=msg.party_id)
        self.event_manager.send(req)

    def on_party_join_event(self, msg: PartyJoinEvent):
        self.event_manager.on(
            FightAutoJoinActivationResponse,
            partial(self.on_fight_auto_join_activation_response),
            originator=self,
            once=True,
        )
        req = FightAutoJoinActivationRequest()
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))

    def on_fight_auto_join_activation_response(
        self, msg: FightAutoJoinActivationResponse
    ):
        self.shared_subjects.leader_target_map_id.connect(
            self.on_new_target_map_id, originator=self
        )
        self.shared_subjects.full_pods.connect(
            self.on_full_pods_signal, originator=self
        )
        self.event_manager.on(
            ContextCreationEvent, self.on_context_creation_event, originator=self
        )
        self.ready_barrier.on_ready(originator=self)

    def on_full_pods_signal(self):
        if self.unload_behavior.is_running.is_set():
            return
        self.unload_behavior.start(
            parent=self, callback=self.on_unload_behavior_finished
        )

    def on_unload_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.ready_barrier.on_ready(originator=self)

    def on_context_creation_event(self, msg: ContextCreationEvent):
        if msg.context == ContextCreationEvent.GameContext.FIGHT:
            self.fight_behavior.start(
                callback=self.on_fight_behavior_finished, parent=self
            )

    def on_fight_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        if self.game_state.inventory.is_full_pods:
            self.shared_subjects.full_pods.emit()
            return self.unload_behavior.start(
                parent=self, callback=self.on_unload_behavior_finished
            )
        self.ready_barrier.on_ready(originator=self)

    def on_new_target_map_id(self, map_id: int):
        if self.auto_trip_smart_behavior.is_running.is_set():
            self.logger.info(
                f"Stopping current auto trip to go map of leader : {map_id}"
            )
            self.auto_trip_smart_behavior.stop()
        self.logger.info(f"Mule is going to {map_id} !")
        self.auto_trip_smart_behavior.start(
            map_ids={map_id},
            parent=self,
            callback=self.on_auto_trip_smart_behavior,
        )

    def on_auto_trip_smart_behavior(self, error_code: str | None):
        self.logger.info("Mule has arrived !")
        if error_code is AutoTripErrorCode.PATH_NOT_FOUND:
            self.logger.info(f"Mule is lost ?")
            return self.finish()
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.ready_barrier.on_ready(originator=self)
