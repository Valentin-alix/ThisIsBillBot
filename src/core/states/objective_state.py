import dataclasses
from dataclasses import dataclass

from db_dofus_unity.protos.game.achievement_pb2 import AchievedAchievement
from db_dofus_unity.protos.game.quest_pb2 import QuestActive, QuestsEvent
from src.core.states.state import State


@dataclass
class ObjectiveState(State):
    active_quest_by_id: dict[int, QuestActive] = dataclasses.field(
        init=False, default_factory=dict
    )
    finished_quest_by_id: dict[int, QuestsEvent.QuestFinished] = dataclasses.field(
        init=False, default_factory=dict
    )
    finished_achievement_by_id: dict[int, AchievedAchievement] = dataclasses.field(
        init=False, default_factory=dict
    )
