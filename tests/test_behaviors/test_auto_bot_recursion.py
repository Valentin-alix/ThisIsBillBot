from datetime import datetime, timedelta
from threading import Timer
from unittest.mock import Mock

import pytest
from ankama_launcher_emulator_premium.interfaces.zaap_files import GameSubscription

from src.core.behaviors.farms.auto_bot_behavior import AutoBotBehavior
from src.core.behaviors.farms.base_farm_behavior import BaseFarmingErrorCode
from tests.fixtures.bot_runtime import EventManagerLockFake
from tests.fixtures.game_state import GameStateContext


def _make_auto_bot(
    game_state_ctx: GameStateContext,
    fighter_behavior: Mock | None = None,
) -> AutoBotBehavior:
    return AutoBotBehavior(
        event_manager=EventManagerLockFake(),  # type: ignore[arg-type]
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        fighter_behavior=fighter_behavior or Mock(),
        harvester_behavior=Mock(),
        multi_farming_behavior=Mock(),
    )


def _cancel_timers(behavior: AutoBotBehavior) -> None:
    for timer in behavior.timers:
        timer.cancel()


def _set_subscribed(monkeypatch: pytest.MonkeyPatch, *, subscribed: bool) -> None:
    def fake_get_game_sub_info(login: str) -> GameSubscription:
        del login
        return GameSubscription(
            isFreeToPlay=not subscribed,
            isFormerSubscriber=False,
            isSubscribed=subscribed,
            totalPlayTime=0,
            endOfSubscribe=datetime.now() + timedelta(days=1)
            if subscribed
            else datetime.now() - timedelta(days=1),
            id=1,
        )

    monkeypatch.setattr(
        "src.core.states.player_state.get_game_sub_info_by_login",
        fake_get_game_sub_info,
    )


def test_restart_after_stop_condition_is_deferred_not_recursive(
    game_state_ctx: GameStateContext,
) -> None:
    """The fighter restart must be scheduled on a timer, never called inline, so
    an immediate stop condition cannot recurse into a RecursionError."""
    behavior = _make_auto_bot(game_state_ctx)
    behavior.play = Mock()  # type: ignore[method-assign]

    behavior.on_fighter_behavior_finished(
        BaseFarmingErrorCode.STOP_CONDITION_TRIGGERED
    )

    behavior.play.assert_not_called()
    assert len(behavior.timers) == 1
    assert isinstance(behavior.timers[0], Timer)
    _cancel_timers(behavior)


def test_no_bank_fighter_does_not_stop_immediately_when_leveled(
    game_state_ctx: GameStateContext,
) -> None:
    """A no-bank fighter past the harvest level/kamas thresholds must not trigger
    its stop condition immediately (which previously caused the tight restart
    loop / RecursionError)."""
    # autouse game_sub_info_mock leaves the player not subscribed -> no bank.
    assert game_state_ctx.game_state.player.can_use_bank is False
    game_state_ctx.game_state.player.level = 200
    game_state_ctx.game_state.inventory.kamas = 1_000_000

    fighter = Mock()
    behavior = _make_auto_bot(game_state_ctx, fighter_behavior=fighter)
    behavior._get_fighter_area_info = Mock(  # type: ignore[method-assign]
        return_value=Mock(area_id=1, sub_area_id=None)
    )

    behavior.play_fighter()

    stop_condition = fighter.start.call_args.kwargs["is_stopped_at_new_map_condition"]
    assert stop_condition() is False
    _cancel_timers(behavior)


def test_with_bank_fighter_still_stops_on_harvest_threshold(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With bank access, reaching the level/kamas thresholds must still trigger the
    stop condition (so the bot switches to harvesting) -- unchanged behavior."""
    _set_subscribed(monkeypatch, subscribed=True)
    assert game_state_ctx.game_state.player.can_use_bank is True
    game_state_ctx.game_state.player.level = 200
    game_state_ctx.game_state.inventory.kamas = 1_000_000

    fighter = Mock()
    behavior = _make_auto_bot(game_state_ctx, fighter_behavior=fighter)
    behavior._get_fighter_area_info = Mock(  # type: ignore[method-assign]
        return_value=Mock(area_id=1, sub_area_id=None)
    )

    behavior.play_fighter()

    stop_condition = fighter.start.call_args.kwargs["is_stopped_at_new_map_condition"]
    assert stop_condition() is True
    _cancel_timers(behavior)
