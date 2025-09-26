"""Un combat en cours ou un donjon non quitte doit etre resolu avant de continuer."""

from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

from context_pb2 import ContextCreationEvent
from datas.protos.non_obf.game.gamemap_pb2 import MapComplementaryInformationEvent
from datas.protos.non_obf.game.haven_bag_pb2 import HavenBagEnterRequest
from google.protobuf.message import Message

from dofus_unity_reader.game_constants.map_id import MapIdEnum

from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.engine.dungeons.dungeon_info import (
    BOUFTOU_ROYAL_DUNGEON,
    get_dungeon_info_for_map_id,
)
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext

OUTSIDE_MAP_ID = 88090898


def _mock_of(behavior: object) -> MagicMock:
    return cast(MagicMock, behavior)


def _make_behavior(
    game_state_ctx: GameStateContext,
    map_id: int,
    sent_messages: list[Message] | None = None,
) -> UnloadBehavior:
    game_state_ctx.game_state.map.map_id = map_id
    event_manager = EventManager(_logger=game_state_ctx.logger)
    if sent_messages is not None:
        event_manager.on_send_game_callback = sent_messages.append
    return UnloadBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        recovery=make_blocking_state_recovery(),
        unload_in_bank_behavior=MagicMock(),
        unload_in_guild_chest_behavior=MagicMock(),
    )


def _callback_of(behavior: object) -> Callable[..., None]:
    return cast(Callable[..., None], _mock_of(behavior).start.call_args.kwargs["callback"])


def _inside_dungeon_map_id() -> int:
    return next(iter(BOUFTOU_ROYAL_DUNGEON.dungeon.mapIds))


def test_a_map_inside_a_dungeon_is_recognised() -> None:
    assert get_dungeon_info_for_map_id(_inside_dungeon_map_id()) is BOUFTOU_ROYAL_DUNGEON


def test_the_exit_map_is_recognised() -> None:
    exit_map_id = BOUFTOU_ROYAL_DUNGEON.exit_dialog_map_id

    assert get_dungeon_info_for_map_id(exit_map_id) is BOUFTOU_ROYAL_DUNGEON


def test_a_map_outside_any_dungeon_is_not_recognised() -> None:
    assert get_dungeon_info_for_map_id(OUTSIDE_MAP_ID) is None


def test_nothing_blocking_runs_the_work_right_away(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx, OUTSIDE_MAP_ID)

    behavior.start(callback=None, parent=None)

    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_called_once()
    _mock_of(behavior.recovery.fight_behavior).start.assert_not_called()
    _mock_of(behavior.recovery.dungeon_behavior).start.assert_not_called()


def test_a_running_fight_is_played_before_the_work(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx, OUTSIDE_MAP_ID)
    game_state_ctx.game_state.fight.in_fight = True

    behavior.start(callback=None, parent=None)

    _mock_of(behavior.recovery.fight_behavior).start.assert_called_once()
    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_not_called()

    game_state_ctx.game_state.fight.in_fight = False
    _callback_of(behavior.recovery.fight_behavior)(None)

    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_called_once()


def test_being_stuck_in_a_dungeon_leaves_it_before_the_work(
    game_state_ctx: GameStateContext,
) -> None:
    """La clef etant consommee a l'entree, le donjon se deduit de la map, pas de l'inventaire."""
    behavior = _make_behavior(game_state_ctx, _inside_dungeon_map_id())

    behavior.start(callback=None, parent=None)

    start_call = _mock_of(behavior.recovery.dungeon_behavior).start.call_args
    assert start_call.kwargs["dungeon_info"] is BOUFTOU_ROYAL_DUNGEON
    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_not_called()

    game_state_ctx.game_state.map.map_id = OUTSIDE_MAP_ID
    start_call.kwargs["callback"](None)

    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_called_once()


def test_a_fight_starting_mid_run_is_played_then_the_work_is_replayed(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx, OUTSIDE_MAP_ID)
    behavior.start(callback=None, parent=None)
    unload_in_guild_chest = _mock_of(behavior.unload_in_guild_chest_behavior)
    assert unload_in_guild_chest.start.call_count == 1

    behavior.event_manager.process_msg(ContextCreationEvent(context=ContextCreationEvent.GameContext.FIGHT))

    _mock_of(behavior.recovery.fight_behavior).start.assert_called_once()

    _callback_of(behavior.recovery.fight_behavior)(None)

    assert unload_in_guild_chest.start.call_count == 2


def test_a_non_fight_context_is_ignored(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx, OUTSIDE_MAP_ID)
    behavior.start(callback=None, parent=None)

    behavior.event_manager.process_msg(
        ContextCreationEvent(context=ContextCreationEvent.GameContext.ROLE_PLAY)
    )

    _mock_of(behavior.recovery.fight_behavior).start.assert_not_called()


def test_being_stuck_in_the_haven_bag_leaves_it_before_the_work(
    game_state_ctx: GameStateContext,
) -> None:
    sent_messages: list[Message] = []
    behavior = _make_behavior(game_state_ctx, OUTSIDE_MAP_ID, sent_messages)
    game_state_ctx.game_state.map.is_in_haven_bag = True

    behavior.start(callback=None, parent=None)

    assert [type(message) for message in sent_messages] == [HavenBagEnterRequest]
    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_not_called()

    game_state_ctx.game_state.map.is_in_haven_bag = False
    behavior.event_manager.process_msg(MapComplementaryInformationEvent(map_id=OUTSIDE_MAP_ID))

    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_called_once()


def test_being_outside_the_haven_bag_sends_no_request(game_state_ctx: GameStateContext) -> None:
    sent_messages: list[Message] = []
    behavior = _make_behavior(game_state_ctx, OUTSIDE_MAP_ID, sent_messages)

    behavior.start(callback=None, parent=None)

    assert sent_messages == []
    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_called_once()


def test_a_fight_inside_a_dungeon_is_played_before_leaving_it(
    game_state_ctx: GameStateContext,
) -> None:
    """Sinon on cherchait des groupes en roleplay pendant le combat en cours."""
    behavior = _make_behavior(game_state_ctx, _inside_dungeon_map_id())
    game_state_ctx.game_state.fight.in_fight = True

    behavior.start(callback=None, parent=None)

    _mock_of(behavior.recovery.fight_behavior).start.assert_called_once()
    _mock_of(behavior.recovery.dungeon_behavior).start.assert_not_called()


def test_being_stuck_on_the_tutorial_map_goes_through_it_first(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx, MapIdEnum.TUTORIAL_STARTING)

    behavior.start(callback=None, parent=None)

    _mock_of(behavior.recovery.tutorial_behavior).start.assert_called_once()
    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_not_called()

    game_state_ctx.game_state.map.map_id = OUTSIDE_MAP_ID
    _callback_of(behavior.recovery.tutorial_behavior)(None)

    _mock_of(behavior.unload_in_guild_chest_behavior).start.assert_called_once()
