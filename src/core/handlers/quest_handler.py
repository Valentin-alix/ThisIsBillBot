from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.quest_pb2 import QuestsEvent
from src.core.handlers.handler import Handler
from src.core.states.quest_state import QuestState


@dataclass
class QuestHandler(Handler):
    quest_state: QuestState

    def __post_init__(self):
        self.msg_event.received_game_msg.connect(self.on_quest_event, QuestsEvent)

    def on_quest_event(self, _, message: QuestsEvent):
        self.quest_state.active_quest_by_id = {
            active_quest.quest_id: active_quest
            for active_quest in message.active_quests
        }
        self.quest_state.finished_quest_by_id = {
            finished_quest.quest_id: finished_quest
            for finished_quest in message.finished_quests
        }
