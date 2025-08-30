from dataclasses import dataclass

from datas.protos.non_obf.game.quest_pb2 import (
    QuestObjectiveValidatedEvent,
    QuestsEvent,
    QuestStartedEvent,
    QuestStepInformationEvent,
    QuestStepStartedEvent,
    QuestStepValidatedEvent,
    QuestValidatedEvent,
)

from src.core.frames.frame import Frame


@dataclass
class QuestFrame(Frame):
    def __post_init__(self) -> None:
        self.game_info_signals.disconnected.connect(self.game_state.quest.clear_state)
        self.event_manager.on(
            QuestsEvent,
            self.on_quests_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            QuestStartedEvent,
            self.on_quest_started_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            QuestValidatedEvent,
            self.on_quest_validated_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            QuestStepStartedEvent,
            self.on_quest_step_started_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            QuestStepValidatedEvent,
            self.on_quest_step_validated_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            QuestObjectiveValidatedEvent,
            self.on_quest_objective_validated_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            QuestStepInformationEvent,
            self.on_quest_step_information_event,
            originator=self,
            priority=self.priority,
        )

    def on_quests_event(self, msg: QuestsEvent) -> None:
        self.game_state.quest.set_active_quests(list(msg.active_quests))
        self.game_state.quest.finished_count_by_quest_id = {
            finished.quest_id: finished.finished_count for finished in msg.finished_quests
        }
        for quest_id in msg.reinitialized_done_quests_id:
            self.game_state.quest.finished_count_by_quest_id.pop(quest_id, None)

    def on_quest_started_event(self, msg: QuestStartedEvent) -> None:
        self.logger.info(f"Quest {msg.quest_id} started")
        self.game_state.quest.set_current_step_id(msg.quest_id, 0)

    def on_quest_validated_event(self, msg: QuestValidatedEvent) -> None:
        self.logger.info(f"Quest {msg.quest_id} validated")
        self.game_state.quest.remove_active_quest(msg.quest_id)
        count = self.game_state.quest.finished_count_by_quest_id.get(msg.quest_id, 0)
        self.game_state.quest.finished_count_by_quest_id[msg.quest_id] = count + 1

    def on_quest_step_started_event(self, msg: QuestStepStartedEvent) -> None:
        self.game_state.quest.set_current_step_id(msg.quest_id, msg.step_id)

    def on_quest_step_validated_event(self, msg: QuestStepValidatedEvent) -> None:
        self.logger.debug(f"Quest {msg.quest_id} step {msg.step_id} validated")

    def on_quest_objective_validated_event(self, msg: QuestObjectiveValidatedEvent) -> None:
        self.game_state.quest.mark_objective_reached(msg.quest_id, msg.objective_id)

    def on_quest_step_information_event(self, msg: QuestStepInformationEvent) -> None:
        self.game_state.quest.update_active_quest(msg.information)
