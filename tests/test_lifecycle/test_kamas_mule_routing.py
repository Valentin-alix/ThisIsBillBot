from typing import cast
from unittest.mock import Mock, patch

import pytest

from src.controller.bot_config import BotConfig, BotConfigService
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator


def _mock(value: object) -> Mock:
    return cast(Mock, value)


@pytest.mark.parametrize(
    ("level", "is_former_sub"),
    [(49, True), (50, False)],
)
def test_unprepared_kamas_mule_uses_auto_bot(
    behavior_coordinator: BehaviorCoordinator,
    level: int,
    is_former_sub: bool,
) -> None:
    behavior_coordinator.player_state = Mock(
        level=level,
        is_former_sub=is_former_sub,
    )
    _mock(behavior_coordinator.get_bot_config).return_value = BotConfig(schedule_profile="M")

    with patch.object(BotConfigService, "is_kamas_mule", return_value=True):
        behavior_coordinator.guess_bot_action()

    _mock(behavior_coordinator.bot_signals.play_auto_bot.emit).assert_called_once()
    _mock(behavior_coordinator.bot_signals.play_mule_kamas.emit).assert_not_called()


def test_prepared_kamas_mule_uses_mule_behavior(
    behavior_coordinator: BehaviorCoordinator,
) -> None:
    behavior_coordinator.player_state = Mock(level=50, is_former_sub=True)
    _mock(behavior_coordinator.get_bot_config).return_value = BotConfig(schedule_profile="M")

    with patch.object(BotConfigService, "is_kamas_mule", return_value=True):
        behavior_coordinator.guess_bot_action()

    _mock(behavior_coordinator.bot_signals.play_mule_kamas.emit).assert_called_once()
    _mock(behavior_coordinator.bot_signals.play_auto_bot.emit).assert_not_called()
