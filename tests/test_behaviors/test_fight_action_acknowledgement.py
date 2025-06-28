from threading import Event
from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightEvent,
    SequenceEndEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import MapMovementEvent, MapMovementRequest
from datas.protos.non_obf.game.fight_pb2 import FightTurnFinishRequest
from dofus_unity_reader.grid.map_point import MapPoint
from google.protobuf.message import Message

from src.core.bot.bot import Bot
from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.farms.fight.fight_movement_behavior import (
    FightMovementBehavior,
)
from src.core.behaviors.farms.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.farms.fight.fight_turn_behavior import FightTurnBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripErrorCode
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.events_manager.event_manager import EventManager
from src.core.frames.entity_frame import EntityFrame
from src.core.states.game_state import GameState
from src.services.human_timings import HumanTimingsService
from tests.fixtures.game_state import GameStateContext, set_game_state

PLAYER_ID = -1
OTHER_FIGHTER_ID = -2


def _make_event_manager(game_state_ctx: GameStateContext) -> EventManager:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    return event_manager


def _register_entity_frame(
    event_manager: EventManager, game_state_ctx: GameStateContext
) -> None:
    EntityFrame(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        is_playing_event=Event(),
        _logger=game_state_ctx.logger,
    )


def _make_fight_move_path(start_cell_id: int, end_cell_id: int) -> MovementPath:
    path_elements = MovementPath.get_path_elements_from_cells(
        [start_cell_id, end_cell_id]
    )
    return MovementPath(
        start=MapPoint.from_cell_id(start_cell_id),
        end=MapPoint.from_cell_id(end_cell_id),
        path=path_elements,
    )


def _set_player_cell(game_state: GameState, cell_id: int) -> None:
    actor = game_state.entity.actor_by_id[PLAYER_ID]
    game_state.entity.update_actor_disposition(
        actor_id=PLAYER_ID,
        direction=actor.disposition.direction,
        cell_id=cell_id,
    )


def _get_delayed_micro_jitter(service: HumanTimingsService, action_name: str) -> float:
    del service, action_name
    return 60.0


class TestFightActionAcknowledgement:
    def test_fight_movement_stops_when_player_dies_before_late_ack(
        self, game_state_ctx: GameStateContext
    ) -> None:
        set_game_state(game_state_ctx.game_state, player_cell_id=345, enemy_cell_ids=[])
        game_state_ctx.game_state.fight.in_fight = True
        event_manager = _make_event_manager(game_state_ctx)
        _register_entity_frame(event_manager, game_state_ctx)
        map_move_behavior = MapMoveBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            path_finding=game_state_ctx.pathfinding,
            _logger=game_state_ctx.logger,
        )
        fight_movement_behavior = FightMovementBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            map_move_behavior=map_move_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_reachable_cells=game_state_ctx.fight_reachable_cells,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []

        fight_movement_behavior.start(
            callback=finished_error_codes.append,
            parent=None,
            move_path=_make_fight_move_path(345, 358),
        )

        event_manager.process_msg(
            MapMovementEvent(cells=[345, 358], character_id=PLAYER_ID)
        )
        event_manager.process_msg(SequenceEndEvent(action_id=12, author_id=PLAYER_ID))
        event_manager.process_msg(
            GameActionFightEvent(
                source_id=OTHER_FIGHTER_ID,
                death=GameActionFightEvent.Death(
                    source_id=OTHER_FIGHTER_ID,
                    target_id=PLAYER_ID,
                ),
            )
        )

        assert PLAYER_ID not in game_state_ctx.game_state.entity.actor_by_id
        assert finished_error_codes == [MapMoveError.PLAYER_DEAD]
        assert fight_movement_behavior.state == BehaviorState.STOPPED
        assert map_move_behavior.state == BehaviorState.STOPPED
        event_manager.process_msg(
            GameActionAcknowledgementRequest(valid=True, action_id=12)
        )

        assert finished_error_codes == [MapMoveError.PLAYER_DEAD]

    def test_fight_movement_finishes_on_latest_player_ack_without_sequence_type(
        self, game_state_ctx: GameStateContext
    ) -> None:
        set_game_state(game_state_ctx.game_state, player_cell_id=399, enemy_cell_ids=[])
        game_state_ctx.game_state.fight.in_fight = True
        event_manager = _make_event_manager(game_state_ctx)
        movement_behavior = MapMoveBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            path_finding=game_state_ctx.pathfinding,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []

        movement_behavior.start(
            callback=finished_error_codes.append,
            parent=None,
            move_path=_make_fight_move_path(399, 412),
        )

        event_manager.process_msg(
            MapMovementEvent(cells=[399, 412], character_id=PLAYER_ID)
        )
        _set_player_cell(game_state_ctx.game_state, 412)
        event_manager.process_msg(
            SequenceEndEvent(
                action_id=6,
                author_id=PLAYER_ID,
                sequence_type="SPELL",
            )
        )
        event_manager.process_msg(
            SequenceEndEvent(
                action_id=8,
                author_id=PLAYER_ID,
                sequence_type="SPELL",
            )
        )
        event_manager.process_msg(
            GameActionAcknowledgementRequest(valid=True, action_id=6)
        )

        assert finished_error_codes == []
        assert movement_behavior.state == BehaviorState.RUNNING

        event_manager.process_msg(
            GameActionAcknowledgementRequest(valid=True, action_id=8)
        )

        assert finished_error_codes == [None]
        assert movement_behavior.state == BehaviorState.STOPPED

    def test_spell_finishes_on_latest_player_ack_and_ignores_other_authors(
        self, game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            HumanTimingsService,
            "get_micro_jitter",
            _get_delayed_micro_jitter,
        )
        set_game_state(game_state_ctx.game_state, player_cell_id=399, enemy_cell_ids=[])
        event_manager = _make_event_manager(game_state_ctx)
        spell_behavior = FightSpellBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []

        spell_behavior.start(
            callback=finished_error_codes.append,
            parent=None,
            spell_id=13242,
            target_mp=MapPoint.from_cell_id(383),
        )

        event_manager.process_msg(
            SequenceEndEvent(action_id=12, author_id=OTHER_FIGHTER_ID)
        )
        event_manager.process_msg(
            GameActionAcknowledgementRequest(valid=True, action_id=12)
        )
        event_manager.process_msg(SequenceEndEvent(action_id=6, author_id=PLAYER_ID))
        event_manager.process_msg(SequenceEndEvent(action_id=16, author_id=PLAYER_ID))
        event_manager.process_msg(
            GameActionAcknowledgementRequest(valid=True, action_id=6)
        )

        assert finished_error_codes == []
        assert spell_behavior.state == BehaviorState.RUNNING

        event_manager.process_msg(
            GameActionAcknowledgementRequest(valid=True, action_id=16)
        )

        assert finished_error_codes == [None]
        assert spell_behavior.state == BehaviorState.STOPPED

    def test_spell_stops_when_player_dies_before_late_ack(
        self, game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            HumanTimingsService,
            "get_micro_jitter",
            _get_delayed_micro_jitter,
        )
        set_game_state(game_state_ctx.game_state, player_cell_id=399, enemy_cell_ids=[])
        event_manager = _make_event_manager(game_state_ctx)
        _register_entity_frame(event_manager, game_state_ctx)
        spell_behavior = FightSpellBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []

        spell_behavior.start(
            callback=finished_error_codes.append,
            parent=None,
            spell_id=13242,
            target_mp=MapPoint.from_cell_id(383),
        )
        event_manager.process_msg(SequenceEndEvent(action_id=16, author_id=PLAYER_ID))
        event_manager.process_msg(
            GameActionFightEvent(
                source_id=OTHER_FIGHTER_ID,
                death=GameActionFightEvent.Death(
                    source_id=OTHER_FIGHTER_ID,
                    target_id=PLAYER_ID,
                ),
            )
        )

        assert finished_error_codes == [MapMoveError.PLAYER_DEAD]
        assert spell_behavior.state == BehaviorState.STOPPED

        event_manager.process_msg(
            GameActionAcknowledgementRequest(valid=True, action_id=16)
        )

        assert finished_error_codes == [MapMoveError.PLAYER_DEAD]

    def test_fight_turn_stops_when_player_dies(
        self, game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        set_game_state(game_state_ctx.game_state, player_cell_id=399, enemy_cell_ids=[])
        event_manager = _make_event_manager(game_state_ctx)
        map_move_behavior = MapMoveBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            path_finding=game_state_ctx.pathfinding,
            _logger=game_state_ctx.logger,
        )
        fight_movement_behavior = FightMovementBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            map_move_behavior=map_move_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_reachable_cells=game_state_ctx.fight_reachable_cells,
            _logger=game_state_ctx.logger,
        )
        fight_spell_behavior = FightSpellBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        fight_turn_behavior = FightTurnBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            fight_movement_behavior=fight_movement_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_spell_behavior=fight_spell_behavior,
            attacker=game_state_ctx.attacker,
            _logger=game_state_ctx.logger,
        )
        monkeypatch.setattr(
            fight_turn_behavior,
            "try_self_buff_or_continue",
            lambda: None,
        )
        finished_error_codes: list[str | None] = []
        fight_turn_behavior.start(callback=finished_error_codes.append, parent=None)

        event_manager.process_msg(
            GameActionFightEvent(
                source_id=OTHER_FIGHTER_ID,
                death=GameActionFightEvent.Death(
                    source_id=OTHER_FIGHTER_ID,
                    target_id=PLAYER_ID,
                ),
            )
        )

        assert finished_error_codes == [MapMoveError.PLAYER_DEAD]
        assert fight_turn_behavior.state is BehaviorState.STOPPED

    def test_fight_turn_does_not_read_map_point_after_player_actor_was_removed(
        self, game_state_ctx: GameStateContext
    ) -> None:
        set_game_state(game_state_ctx.game_state, player_cell_id=399, enemy_cell_ids=[])
        game_state_ctx.game_state.entity.remove_actor(PLAYER_ID)
        event_manager = _make_event_manager(game_state_ctx)
        map_move_behavior = MapMoveBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            path_finding=game_state_ctx.pathfinding,
            _logger=game_state_ctx.logger,
        )
        fight_movement_behavior = FightMovementBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            map_move_behavior=map_move_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_reachable_cells=game_state_ctx.fight_reachable_cells,
            _logger=game_state_ctx.logger,
        )
        fight_spell_behavior = FightSpellBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        fight_turn_behavior = FightTurnBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            fight_movement_behavior=fight_movement_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_spell_behavior=fight_spell_behavior,
            attacker=game_state_ctx.attacker,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []

        fight_turn_behavior.start(callback=finished_error_codes.append, parent=None)

        assert finished_error_codes == [MapMoveError.PLAYER_DEAD]
        assert fight_turn_behavior.state is BehaviorState.STOPPED

    def test_fight_turn_passes_without_runaway_when_no_enemies_remain(
        self, game_state_ctx: GameStateContext
    ) -> None:
        set_game_state(game_state_ctx.game_state, player_cell_id=344, enemy_cell_ids=[])
        game_state_ctx.game_state.fight.in_fight = True
        event_manager = _make_event_manager(game_state_ctx)
        sent_messages: list[Message] = []
        event_manager.on_send_game_callback = sent_messages.append
        map_move_behavior = MapMoveBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            path_finding=game_state_ctx.pathfinding,
            _logger=game_state_ctx.logger,
        )
        fight_movement_behavior = FightMovementBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            map_move_behavior=map_move_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_reachable_cells=game_state_ctx.fight_reachable_cells,
            _logger=game_state_ctx.logger,
        )
        fight_spell_behavior = FightSpellBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        fight_turn_behavior = FightTurnBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            fight_movement_behavior=fight_movement_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_spell_behavior=fight_spell_behavior,
            attacker=game_state_ctx.attacker,
            _logger=game_state_ctx.logger,
        )
        fight_turn_behavior.did_attack = True

        fight_turn_behavior.find_and_do_attack()

        assert [type(sent_message) for sent_message in sent_messages] == [
            FightTurnFinishRequest
        ]
        assert map_move_behavior.state == BehaviorState.STOPPED

    def test_runaway_finishes_without_movement_when_no_enemies_remain(
        self, game_state_ctx: GameStateContext
    ) -> None:
        set_game_state(game_state_ctx.game_state, player_cell_id=344, enemy_cell_ids=[])
        game_state_ctx.game_state.fight.in_fight = True
        event_manager = _make_event_manager(game_state_ctx)
        sent_messages: list[Message] = []
        event_manager.on_send_game_callback = sent_messages.append
        map_move_behavior = MapMoveBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            path_finding=game_state_ctx.pathfinding,
            _logger=game_state_ctx.logger,
        )
        fight_movement_behavior = FightMovementBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            map_move_behavior=map_move_behavior,
            path_finding=game_state_ctx.pathfinding,
            fight_reachable_cells=game_state_ctx.fight_reachable_cells,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []

        fight_movement_behavior.start(
            callback=finished_error_codes.append,
            parent=None,
            run_away=True,
        )

        assert finished_error_codes == [None]
        assert not any(
            isinstance(sent_message, MapMovementRequest)
            for sent_message in sent_messages
        )
        assert fight_movement_behavior.state == BehaviorState.STOPPED
        assert map_move_behavior.state == BehaviorState.STOPPED


class TestFarmRecovery:
    def test_incomplete_fight_initialization_requests_disconnect(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        attacker_behavior = runtime_bot.fighter_behavior.attacker_behavior
        request_disconnect = MagicMock()
        attack_enemy = MagicMock()
        runtime_bot.game_state.fight.in_fight = True
        runtime_bot.event_manager.request_disconnect_callback = request_disconnect
        monkeypatch.setattr(attacker_behavior, "attack_enemy", attack_enemy)

        attacker_behavior.on_fight_map_information_timeout(-20_003)

        request_disconnect.assert_called_once_with()
        attack_enemy.assert_not_called()

    def test_path_blocked_by_forbidden_transition_requests_disconnect(
        self, runtime_bot: Bot
    ) -> None:
        random_farm_behavior = runtime_bot.fighter_behavior.random_farm_behavior
        request_disconnect = MagicMock()
        runtime_bot.event_manager.request_disconnect_callback = request_disconnect
        runtime_bot.game_state.map.forbidden_edge_transitions.add(
            (MagicMock(), MagicMock(), MagicMock())
        )

        random_farm_behavior.on_auto_trip_world_behavior_finished(
            AutoTripErrorCode.PATH_NOT_FOUND
        )

        request_disconnect.assert_called_once_with()
