from unittest.mock import Mock

from src.core.bot.bot import Bot
from src.services.sandbox.executor import SandboxExecutor


def test_run_returns_last_expression_repr(runtime_bot: Bot) -> None:
    result = SandboxExecutor(bot=runtime_bot).run("1 + 1")
    assert result.result_repr == "2"
    assert result.error is None


def test_run_captures_stdout(runtime_bot: Bot) -> None:
    result = SandboxExecutor(bot=runtime_bot).run("print('hi')")
    assert result.stdout == "hi\n"
    assert result.error is None


def test_run_catches_exceptions(runtime_bot: Bot) -> None:
    result = SandboxExecutor(bot=runtime_bot).run("1 / 0")
    assert result.error is not None
    assert "ZeroDivisionError" in result.error


def test_run_exposes_bot_and_game_state(runtime_bot: Bot) -> None:
    result = SandboxExecutor(bot=runtime_bot).run("bot is not None and game_state is bot.game_state")
    assert result.result_repr == "True"
    assert result.error is None


def test_send_message_helper_sends_through_event_manager(runtime_bot: Bot) -> None:
    runtime_bot.event_manager.send = Mock()  # type: ignore[method-assign]
    executor = SandboxExecutor(bot=runtime_bot)

    executor.send_message("BasicLatencyStatsRequest")

    runtime_bot.event_manager.send.assert_called_once()
    (sent_message,) = runtime_bot.event_manager.send.call_args.args
    assert sent_message.__class__.__name__ == "BasicLatencyStatsRequest"


def test_send_message_helper_rejects_unknown_message(runtime_bot: Bot) -> None:
    result = SandboxExecutor(bot=runtime_bot).run("send_message('NotARealMessage')")
    assert result.error is not None
    assert "Unknown message" in result.error


def test_trigger_behavior_helper_delegates_to_coordinator(runtime_bot: Bot) -> None:
    runtime_bot.behavior_coordinator.on_play_usable_behavior = Mock()  # type: ignore[method-assign]
    behavior_name = runtime_bot.usable_behaviors[0].__class__.__name__

    SandboxExecutor(bot=runtime_bot).trigger_behavior(behavior_name)

    runtime_bot.behavior_coordinator.on_play_usable_behavior.assert_called_once_with(behavior_name)


def test_trigger_behavior_helper_rejects_unknown_name(runtime_bot: Bot) -> None:
    result = SandboxExecutor(bot=runtime_bot).run("trigger_behavior('NotABehavior')")
    assert result.error is not None
    assert "Unknown behavior" in result.error
