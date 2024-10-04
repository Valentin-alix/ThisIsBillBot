import dataclasses
from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.quest_pb2 import QuestActive, QuestsEvent
from src.core.states.state import State


@dataclass
class QuestState(State):
    active_quest_by_id: dict[int, QuestActive] = dataclasses.field(
        init=False, default_factory=lambda: {}
    )
    finished_quest_by_id: dict[int, QuestsEvent.QuestFinished] = dataclasses.field(
        init=False, default_factory=lambda: {}
    )
