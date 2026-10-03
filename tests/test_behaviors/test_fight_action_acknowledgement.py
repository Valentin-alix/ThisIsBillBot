from collections.abc import Callable
from threading import Event, Thread
from typing import cast
from unittest.mock import MagicMock

import pytest
from google.protobuf.message import Message

from DBDofusUnity.datas.protos.non_obf.game.challenge_pb2 import (
    ChallengeProposalEvent,
    ChallengeSelectionRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import Challenge
from DBDofusUnity.datas.protos.non_obf.game.fight_pb2 import FightTurnFinishRequest
from DBDofusUnity.datas.protos.non_obf.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightEvent,
    SequenceEndEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import MapMovementEvent, MapMovementRequest
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem
from DBDofusUnity.dofus_unity_reader.models.world_graph import Edge
from src.core.behaviors.behavior import (
    BehaviorLifecycleError,
    BehaviorState,
    BehaviorStateError,
)
from src.core.behaviors.farms import random_farm_behavior as random_farm_module
from src.core.behaviors.farms.fight.fight_movement_behavior import (
    FightMovementBehavior,
)
from src.core.behaviors.farms.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.farms.fight.fight_turn_behavior import FightTurnBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.bot.bot import Bot
from src.core.engine.contexts import AttackContext
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


def _register_entity_frame(event_manager: EventManager, game_state_ctx: GameStateContext) -> None:
    EntityFrame(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        is_playing_event=Event(),
        _logger=game_state_ctx.logger,
    )


def _make_fight_move_path(start_cell_id: int, end_cell_id: int) -> MovementPath:
    path_elements = MovementPath.get_path_elements_from_cells([start_cell_id, end_cell_id])
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


def _get_fixed_challenge_selection_timing(service: HumanTimingsService) -> float:
    del service
    return 0.03


def _no_self_buff(context: AttackContext) -> SpellLevelsRootItem | None:
    del context
    return None


class TestFightActionAcknowledgement:
    def test_challenge_proposal_selects_first_proposed_challenge(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game_session_behavior = runtime_bot.game_session_behavior
        sent_messages: list[Message] = []
        scheduled_delays: list[float] = []
        runtime_bot.event_manager.on_send_game_callback = sent_messages.append

        def run_timer(delay: float, callback: Callable[[], None]) -> None:
            scheduled_delays.append(delay)
            callback()

        monkeypatch.setattr(game_session_behavior, "run_timer", run_timer)
        monkeypatch.setattr(
            HumanTimingsService,
            "get_timing_fight_challenge_selection",
            _get_fixed_challenge_selection_timing,
        )

        game_session_behavior.run()
        runtime_bot.event_manager.process_msg(
            ChallengeProposalEvent(
                challenge_proposals=[
                    Challenge(challenge_id=8),
                    Challenge(challenge_id=17),
                ]
            )
        )

        assert scheduled_delays == [0.03]
        assert len(sent_messages) == 1
        selection_request = sent_messages[0]
        assert isinstance(selection_request, ChallengeSelectionRequest)
        assert selection_request.challenge_id == 8

    def test_empty_challenge_proposal_leaves_selection_to_server(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game_session_behavior = runtime_bot.game_session_behavior
        run_timer = MagicMock()
        monkeypatch.setattr(game_session_behavior, "run_timer", run_timer)

        game_session_behavior.run()
        runtime_bot.event_manager.process_msg(ChallengeProposalEvent())

        run_timer.assert_not_called()

    def test_start_with_stopped_parent_rolls_back_child_state(
        self,
        runtime_bot: Bot,
    ) -> None:
        random_farm_behavior = runtime_bot.fighter_behavior.random_farm_behavior
        auto_trip_behavior = random_farm_behavior.auto_trip_smart_behavior

        with pytest.raises(BehaviorLifecycleError):
            auto_trip_behavior.start(
                callback=None,
                parent=random_farm_behavior,
                map_ids={runtime_bot.game_state.map.map_id},
            )

        assert auto_trip_behavior.state is BehaviorState.STOPPED
        assert auto_trip_behavior.parent is None

    def test_double_start_raises_instead_of_leaving_silent_stall(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game_session_behavior = runtime_bot.game_session_behavior
        monkeypatch.setattr(game_session_behavior, "run", lambda: None)
        game_session_behavior.start(callback=None, parent=None)

        with pytest.raises(BehaviorStateError):
            game_session_behavior.start(callback=None, parent=None)

        assert game_session_behavior.state is BehaviorState.RUNNING
        game_session_behavior.stop()

    def test_synchronous_run_failure_cleans_behavior_before_propagating(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game_session_behavior = runtime_bot.game_session_behavior

        def raise_run_error() -> None:
            raise RuntimeError("synchronous run failure")

        monkeypatch.setattr(game_session_behavior, "run", raise_run_error)

        with pytest.raises(RuntimeError, match="synchronous run failure"):
            game_session_behavior.start(callback=None, parent=None)

        assert game_session_behavior.state is BehaviorState.STOPPED

    def test_random_farm_publishes_stable_paths_during_concurrent_updates(
        self,
        runtime_bot: Bot,
    ) -> None:
        random_farm_behavior = runtime_bot.fighter_behavior.random_farm_behavior
        runtime_bot.game_state.player.server_id = 1
        runtime_bot.game_state.player.character_id = 10
        edge_mock = MagicMock()
        edge_mock.m_to.m_mapId = 123
        edge = cast(Edge, edge_mock)
        random_farm_behavior.map_ids = {123}
        random_farm_behavior.get_additional_weight_by_map_id = lambda map_id: 0
        original_path = [edge]
        random_farm_behavior.edge_path = original_path
        original_path.clear()

        with random_farm_module.PATH_LOCK:
            published_path = random_farm_module.EDGE_PATH_BY_SERVER_AND_CHARACTER[(1, 10)]
        assert published_path == (edge,)

        competing_key = (1, 20)

        def update_competing_path() -> None:
            for iteration in range(2_000):
                with random_farm_module.PATH_LOCK:
                    if iteration % 2 == 0:
                        random_farm_module.EDGE_PATH_BY_SERVER_AND_CHARACTER[competing_key] = (edge,)
                    else:
                        random_farm_module.EDGE_PATH_BY_SERVER_AND_CHARACTER.pop(competing_key, None)

        writer_thread = Thread(target=update_competing_path)
        writer_thread.start()
        for _weight_calculation_index in range(2_000):
            random_farm_behavior.get_weight_edge(edge)
        writer_thread.join()

        with random_farm_module.PATH_LOCK:
            random_farm_module.EDGE_PATH_BY_SERVER_AND_CHARACTER.pop(competing_key, None)
        random_farm_behavior.edge_path = None

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

        event_manager.process_msg(MapMovementEvent(cells=[345, 358], character_id=PLAYER_ID))
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
        event_manager.process_msg(GameActionAcknowledgementRequest(valid=True, action_id=12))

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

        event_manager.process_msg(MapMovementEvent(cells=[399, 412], character_id=PLAYER_ID))
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
        event_manager.process_msg(GameActionAcknowledgementRequest(valid=True, action_id=6))

        assert finished_error_codes == []
        assert movement_behavior.state == BehaviorState.RUNNING

        event_manager.process_msg(GameActionAcknowledgementRequest(valid=True, action_id=8))

        assert finished_error_codes == [None]
        assert movement_behavior.state == BehaviorState.STOPPED

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
            fight_spell_behavior=fight_spell_behavior,
            attack_selector=game_state_ctx.attacker,
            breed_ability_selector=game_state_ctx.breed_ability_selector,
            _logger=game_state_ctx.logger,
        )
        monkeypatch.setattr(
            fight_turn_behavior.attack_selector,
            "find_best_self_buff",
            _no_self_buff,
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
            fight_spell_behavior=fight_spell_behavior,
            attack_selector=game_state_ctx.attacker,
            breed_ability_selector=game_state_ctx.breed_ability_selector,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []

        fight_turn_behavior.start(callback=finished_error_codes.append, parent=None)

        assert finished_error_codes == [None]
        assert fight_turn_behavior.state is BehaviorState.STOPPED

    def test_fight_turn_spell_callback_finishes_after_victory_removed_player_actor(
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
            fight_spell_behavior=fight_spell_behavior,
            attack_selector=game_state_ctx.attacker,
            breed_ability_selector=game_state_ctx.breed_ability_selector,
            _logger=game_state_ctx.logger,
        )
        finished_error_codes: list[str | None] = []
        monkeypatch.setattr(
            fight_turn_behavior.attack_selector,
            "find_best_self_buff",
            _no_self_buff,
        )
        fight_turn_behavior.start(callback=finished_error_codes.append, parent=None)
        game_state_ctx.game_state.entity.remove_actor(PLAYER_ID)

        fight_turn_behavior.on_fight_spell_behavior_finished(None)

        assert finished_error_codes == [None]
        assert fight_turn_behavior.state is BehaviorState.STOPPED

    def test_fight_turn_passes_without_runaway_when_no_enemies_remain(
        self, game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
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
            fight_spell_behavior=fight_spell_behavior,
            attack_selector=game_state_ctx.attacker,
            breed_ability_selector=game_state_ctx.breed_ability_selector,
            _logger=game_state_ctx.logger,
        )
        fight_turn_behavior.did_attack = True
        monkeypatch.setattr(fight_turn_behavior.attack_selector, "find_best_self_buff", _no_self_buff)

        fight_turn_behavior._advance_turn(0)

        assert [type(sent_message) for sent_message in sent_messages] == [FightTurnFinishRequest]
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

        fight_movement_behavior.start(callback=finished_error_codes.append, parent=None)

        assert finished_error_codes == [None]
        assert not any(isinstance(sent_message, MapMovementRequest) for sent_message in sent_messages)
        assert fight_movement_behavior.state == BehaviorState.STOPPED
        assert map_move_behavior.state == BehaviorState.STOPPED
