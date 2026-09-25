from src.core.bot.bot import Bot


def test_bot_does_not_register_removed_chat_quest_or_achievement_features(runtime_bot: Bot) -> None:
    frame_names = {type(frame).__name__ for frame in runtime_bot.frames}
    usable_behavior_names = {type(behavior).__name__ for behavior in runtime_bot.usable_behaviors}

    assert not frame_names & {"ChatFrame", "QuestFrame", "AchievementFrame"}
    assert not usable_behavior_names & {"SmokeTestBehavior", "QuestBehavior"}
    assert not hasattr(runtime_bot.game_state, "quest")
    assert not hasattr(runtime_bot.auto_bot_behavior, "quest_behavior")
