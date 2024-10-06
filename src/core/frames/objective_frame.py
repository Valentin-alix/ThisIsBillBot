from dataclasses import dataclass

from db_dofus_unity.protos.game.achievement_pb2 import AchievementsEvent
from db_dofus_unity.protos.game.quest_pb2 import QuestsEvent, QuestStepInformationEvent
from src.core.frames.frame import Frame
from src.core.states.objective_state import ObjectiveState


@dataclass
class ObjectiveFrame(Frame):
    objective_state: ObjectiveState

    def __post_init__(self):
        self.event_manager.on(QuestsEvent, self.on_quest_event, originator=self)
        self.event_manager.on(
            AchievementsEvent,
            self.on_achievements_event,
            originator=self,
        )
        self.event_manager.on(
            QuestStepInformationEvent,
            self.on_quest_step_information_event,
            originator=self,
        )

    def on_quest_event(self, message: QuestsEvent):
        self.objective_state.active_quest_by_id = {
            active_quest.quest_id: active_quest
            for active_quest in message.active_quests
        }
        self.objective_state.finished_quest_by_id = {
            finished_quest.quest_id: finished_quest
            for finished_quest in message.finished_quests
        }

    def on_achievements_event(self, message: AchievementsEvent):
        self.objective_state.finished_achievement_by_id = {
            achievement.achievement_id: achievement
            for achievement in message.achieved_achievements
        }

    def on_quest_step_information_event(self, msg: QuestStepInformationEvent):
        self.objective_state.active_quest_by_id[msg.information.quest_id] = (
            msg.information
        )
