from dataclasses import dataclass, field

from DBDofusUnity.datas.protos.non_obf.game.achievement_pb2 import (
    AchievementFinishedEvent,
    AchievementRewardRequest,
    AchievementRewardResultEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import CharacterLevelUpEvent

from src.core.frames.frame import Frame
from src.services.human_timings import HumanTimingsService

ALL_ACHIEVEMENT_REWARDS_ID = -1


@dataclass
class AchievementFrame(Frame):
    _is_collect_scheduled: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self.event_manager.on(
            AchievementFinishedEvent,
            self.on_achievement_finished_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            CharacterLevelUpEvent,
            self.on_character_level_up_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            AchievementRewardResultEvent,
            self.on_achievement_reward_result_event,
            originator=self,
            priority=self.priority,
        )
        self.game_info_signals.disconnected.connect(self.on_disconnected)

    def on_achievement_finished_event(self, msg: AchievementFinishedEvent) -> None:
        self.logger.info(f"Achievement {msg.achievement.achievement_id} finished")
        self.schedule_reward_collect()

    def on_character_level_up_event(self, msg: CharacterLevelUpEvent) -> None:
        self.schedule_reward_collect()

    def schedule_reward_collect(self) -> None:
        if not self.is_playing_event.is_set() or self._is_collect_scheduled:
            return
        self._is_collect_scheduled = True
        self.run_timer(
            HumanTimingsService().get_timing_after_achievement(),
            self.collect_rewards,
        )

    def collect_rewards(self) -> None:
        self._is_collect_scheduled = False
        if not self.is_playing_event.is_set():
            return
        self.logger.info("Collecting every pending achievement reward")
        self.event_manager.send(AchievementRewardRequest(achievement_id=ALL_ACHIEVEMENT_REWARDS_ID))

    def on_achievement_reward_result_event(self, msg: AchievementRewardResultEvent) -> None:
        if msg.success:
            self.logger.info(f"Reward collected for achievement {msg.achievement_id}")
        else:
            self.logger.warning(f"Reward refused for achievement {msg.achievement_id}")

    def on_disconnected(self) -> None:
        super().on_disconnected()
        self._is_collect_scheduled = False
