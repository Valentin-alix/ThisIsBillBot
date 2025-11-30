from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.basic_pb2 import (
    TextInformationEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.dialog_pb2 import DialogLeaveEvent
from DBDofusUnity.datas.protos.non_obf.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    SequenceEndEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import (
    MapMovementConfirmRequest,
    MapMovementConfirmResponse,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapMovementRequest,
)
from DBDofusUnity.dofus_unity_reader.game_constants.text_enum import TextEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from src.core.behaviors.behavior import Behavior
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding

CLIENT_CONFIRM_OVERHEAD = 0.040
WATCHED_ACTOR_MOVED_REDIRECT_DELAY = (0.15, 0.35)


class MapMoveError(StrEnum):
    CANCELED_MOVEMENT = auto()
    INVALID_STARTING_POINT = auto()
    REFUSED = auto()
    CELL_TAKEN = auto()
    UNEXPECTED_NEW_MAP = auto()
    PLAYER_DEAD = auto()
    TARGET_UNREACHABLE = auto()


@dataclass
class MapMoveBehavior(Behavior):
    path_finding: Pathfinding

    _cell_is_taken: bool = field(init=False, default=False)
    _pending_fight_movement_action_id: int | None = field(init=False, default=None)
    _watch_actor_id: int | None = field(init=False, default=None)

    def run(self, move_path: MovementPath, watch_actor_id: int | None = None) -> None:
        self.logger.info(f"Going to : {move_path.end}")
        self._watch_actor_id = watch_actor_id
        if self.game_state.map.is_waiting_for_map_popup_dialog_leave:
            self.logger.info("Waiting for map popup dialog to close before moving")
            self.event_manager.on(
                DialogLeaveEvent,
                lambda _: self.run(move_path=move_path, watch_actor_id=watch_actor_id),
                originator=self,
                once=True,
                override_on_self=True,
                timeout=3,
                on_timeout=lambda: self.run(move_path=move_path, watch_actor_id=watch_actor_id),
            )
            return

        self.ensure_dialog_closed(lambda: self.move_along(move_path))

    def move_along(self, move_path: MovementPath) -> None:
        if self.game_state.map.map_point != move_path.start:
            self.logger.warning(
                f"Player is not at starting move path, he is at {self.game_state.map.map_point}, invalid move path"
            )
            return self.finish(MapMoveError.INVALID_STARTING_POINT)

        if self.game_state.map.map_point.cell_id == move_path.end.cell_id:
            return self.finish()

        key_cells = move_path.get_key_cells()
        if self.game_state.fight.in_fight:
            self._cell_is_taken = False
            self._pending_fight_movement_action_id = None
            self.event_manager.on(TextInformationEvent, self.on_text_information_event, originator=self)
            self.event_manager.on(
                MapMovementEvent,
                callback=partial(
                    self.on_fight_map_movement_event,
                    move_path=move_path,
                ),
                originator=self,
            )
        else:
            self.event_manager.on(
                MapMovementEvent,
                callback=partial(
                    self.on_map_movement_event,
                    move_path=move_path,
                ),
                originator=self,
            )

        self.event_manager.on(
            MapMovementRefusedEvent,
            partial(
                self.on_map_movement_refused_event_after_request,
                start_mp=move_path.start,
            ),
            originator=self,
            once=True,
        )

        map_movement_request = MapMovementRequest(key_cells=key_cells, map_id=self.game_state.map.map_id)
        self.event_manager.send(map_movement_request)

    def on_text_information_event(self, msg: TextInformationEvent):
        if (
            msg.message_type is TextInformationEvent.TextInformationType.TEXT_INFORMATION_ERROR
            and msg.message_id == TextEnum.TAKEN_CELL
        ):
            self._cell_is_taken = True

    def on_fight_map_movement_event(self, msg: MapMovementEvent, move_path: MovementPath) -> None:
        if msg.character_id != self.game_state.player.character_id:
            return
        self.unregister_listener(
            MapMovementEvent, reason="Fight movement started, now waiting for sequence end"
        )
        self._replace_initial_refusal_listener(move_path.end)
        self.event_manager.on(SequenceEndEvent, self.on_sequence_end_event, originator=self)
        self.event_manager.on(
            GameActionAcknowledgementRequest,
            partial(self.on_game_action_acknowledgement_request, move_path=move_path),
            originator=self,
        )

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if msg.author_id == self.game_state.player.character_id:
            self._pending_fight_movement_action_id = msg.action_id

    def on_game_action_acknowledgement_request(
        self,
        msg: GameActionAcknowledgementRequest,
        move_path: MovementPath,
    ):
        if msg.valid and msg.action_id == self._pending_fight_movement_action_id:
            if self._cell_is_taken:
                taken_mp = move_path.get_next_step(self.game_state.map.map_point)
                return self.finish(MapMoveError.CELL_TAKEN, cell_mp=taken_mp)
            if self.game_state.map.map_point != move_path.end:
                self.logger.info("Movement was canceled.")
                return self.finish(MapMoveError.CANCELED_MOVEMENT)
            self.finish()

    def on_map_movement_event(self, msg: MapMovementEvent, move_path: MovementPath) -> None:
        if self.game_state.player.character_id == msg.character_id:
            self.unregister_listener(
                MapMovementEvent, reason="Player movement confirmed, switching to completion listener"
            )
            self._replace_initial_refusal_listener(move_path.end)
            duration = (
                MovementPath.get_total_duration(
                    MovementPath.get_path_elements_from_cells(list(msg.cells)),
                    self.game_state.inventory.inventory_weight,
                    self.game_state.inventory.weight_max,
                )
                + CLIENT_CONFIRM_OVERHEAD
            )
            error_code: str | None
            if move_path.end.cell_id != msg.cells[-1]:
                error_code = MapMoveError.CANCELED_MOVEMENT
                if self.game_state.fight.in_fight:
                    return self.finish(error_code)
            else:
                error_code = None
            self.event_manager.on(
                MapMovementConfirmResponse,
                callback=lambda _: self._on_movement_confirmed(move_path, error_code),
                originator=self,
                once=True,
            )
            self.send_message_delayed(MapMovementConfirmRequest(), duration)

    def _on_movement_confirmed(self, move_path: MovementPath, error_code: str | None) -> None:
        if error_code is not None or self._watch_actor_id is None:
            return self.finish(error_code)

        watched_actor = self.game_state.entity.actor_by_id.get(self._watch_actor_id)
        if watched_actor is None or watched_actor.disposition.cell_id == move_path.end.cell_id:
            return self.finish()

        new_target = MapPoint.from_cell_id(watched_actor.disposition.cell_id)
        new_move_path = self.path_finding.find_path(
            self.game_state.get_map_movement_context(), move_path.end, {new_target}
        )
        if new_move_path.end.cell_id != new_target.cell_id:
            return self.finish(MapMoveError.TARGET_UNREACHABLE)

        self.logger.info(f"Watched actor {self._watch_actor_id} moved, following up to {new_target}")
        self.unregister_listener(MapMovementRefusedEvent, reason="Watched actor moved, redirecting")
        self.run_timer(WATCHED_ACTOR_MOVED_REDIRECT_DELAY, partial(self.move_along, new_move_path))

    def _replace_initial_refusal_listener(self, end_mp: MapPoint) -> None:
        self.unregister_listener(
            MapMovementRefusedEvent,
            reason="Movement accepted, switching to completion refusal listener",
        )
        self.event_manager.on(
            MapMovementRefusedEvent,
            partial(
                self.on_map_movement_refused_event_after_acceptance,
                end_mp=end_mp,
            ),
            originator=self,
            once=True,
        )

    def on_map_movement_refused_event_after_request(
        self, msg: MapMovementRefusedEvent, start_mp: MapPoint
    ) -> None:
        real_mp = MapPoint.from_coords(msg.cell_x, msg.cell_y)
        if real_mp != start_mp:
            return self.finish(MapMoveError.INVALID_STARTING_POINT)
        return self.finish(MapMoveError.REFUSED)

    def on_map_movement_refused_event_after_acceptance(
        self, msg: MapMovementRefusedEvent, end_mp: MapPoint
    ) -> None:
        real_mp = MapPoint.from_coords(msg.cell_x, msg.cell_y)
        if real_mp == end_mp:
            return self.finish()
        return self.finish(MapMoveError.CANCELED_MOVEMENT)
