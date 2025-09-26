from collections.abc import Callable
from threading import Event

from datas.protos.non_obf.game.achievement_pb2 import (
    AchievementFinishedEvent,
    AchievementRewardRequest,
)
from datas.protos.non_obf.game.character_pb2 import CharacterLevelUpEvent
from google.protobuf.message import Message

from src.core.events_manager.event_manager import EventManager
from src.core.frames.achievement_frame import (
    ALL_ACHIEVEMENT_REWARDS_ID,
    AchievementFrame,
)
from tests.fixtures.game_state import GameStateContext

ACHIEVEMENT_ID = 1041


def _make_frame(
    game_state_ctx: GameStateContext, *, is_playing: bool = True
) -> tuple[AchievementFrame, EventManager, list[Message]]:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    is_playing_event = Event()
    if is_playing:
        is_playing_event.set()
    frame = AchievementFrame(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        _logger=game_state_ctx.logger,
        is_playing_event=is_playing_event,
    )

    def run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time
        func()

    frame.run_timer = run_timer_inline
    return frame, event_manager, sent_messages


def _achievement_finished(achievement_id: int = ACHIEVEMENT_ID) -> AchievementFinishedEvent:
    msg = AchievementFinishedEvent()
    msg.achievement.achievement_id = achievement_id
    return msg


def test_a_finished_achievement_claims_every_pending_reward(
    game_state_ctx: GameStateContext,
) -> None:
    _, event_manager, sent_messages = _make_frame(game_state_ctx)

    event_manager.process_msg(_achievement_finished())

    assert [type(message) for message in sent_messages] == [AchievementRewardRequest]
    request = sent_messages[0]
    assert isinstance(request, AchievementRewardRequest)
    assert request.achievement_id == ALL_ACHIEVEMENT_REWARDS_ID


def test_a_level_up_also_claims_the_rewards(game_state_ctx: GameStateContext) -> None:
    _, event_manager, sent_messages = _make_frame(game_state_ctx)

    event_manager.process_msg(CharacterLevelUpEvent(new_level=42))

    assert [type(message) for message in sent_messages] == [AchievementRewardRequest]


def test_a_burst_of_achievements_sends_a_single_request(
    game_state_ctx: GameStateContext,
) -> None:
    frame, event_manager, sent_messages = _make_frame(game_state_ctx)

    def never_fire(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time, func

    frame.run_timer = never_fire

    event_manager.process_msg(_achievement_finished(achievement_id=1))
    event_manager.process_msg(_achievement_finished(achievement_id=2))
    event_manager.process_msg(CharacterLevelUpEvent(new_level=42))

    assert sent_messages == []
    frame.collect_rewards()
    assert [type(message) for message in sent_messages] == [AchievementRewardRequest]


def test_a_new_achievement_after_a_collect_is_claimed_again(
    game_state_ctx: GameStateContext,
) -> None:
    _, event_manager, sent_messages = _make_frame(game_state_ctx)

    event_manager.process_msg(_achievement_finished(achievement_id=1))
    event_manager.process_msg(_achievement_finished(achievement_id=2))

    assert [type(message) for message in sent_messages] == [
        AchievementRewardRequest,
        AchievementRewardRequest,
    ]


def test_nothing_is_claimed_while_the_bot_is_not_playing(
    game_state_ctx: GameStateContext,
) -> None:
    _, event_manager, sent_messages = _make_frame(game_state_ctx, is_playing=False)

    event_manager.process_msg(_achievement_finished())

    assert sent_messages == []
