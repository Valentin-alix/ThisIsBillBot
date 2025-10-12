from dataclasses import dataclass, field

from DBDofusUnity.datas.protos.non_obf.game.quest_pb2 import QuestActive, QuestObjective

from src.core.states.state import State


@dataclass
class QuestState(State):
    active_quest_by_id: dict[int, QuestActive] = field(init=False, default_factory=dict[int, QuestActive])
    finished_count_by_quest_id: dict[int, int] = field(init=False, default_factory=dict[int, int])

    def clear_state(self) -> None:
        self.active_quest_by_id.clear()
        self.finished_count_by_quest_id.clear()

    def set_active_quests(self, quests: list[QuestActive]) -> None:
        self.active_quest_by_id = {quest.quest_id: quest for quest in quests}

    def update_active_quest(self, quest: QuestActive) -> None:
        self.active_quest_by_id[quest.quest_id] = quest

    def remove_active_quest(self, quest_id: int) -> None:
        self.active_quest_by_id.pop(quest_id, None)

    def current_step_id(self, quest_id: int) -> int | None:
        quest = self.active_quest_by_id.get(quest_id)
        if quest is None or not quest.HasField("details"):
            return None
        return quest.details.step_id

    def set_current_step_id(self, quest_id: int, step_id: int) -> None:
        quest = self.active_quest_by_id.setdefault(quest_id, QuestActive(quest_id=quest_id))
        quest.details.step_id = step_id

    def is_active(self, quest_id: int) -> bool:
        return quest_id in self.active_quest_by_id

    def is_objective_reached(self, quest_id: int, objective_id: int) -> bool:
        """Un objectif n'est fait que s'il est envoye avec `objective_reached` a False.

        Le champ porte mal son nom : le serveur le met a True tant que l'objectif reste **a
        faire**, et le bascule a False quand il est valide. Releve sur la quete 1696 :

            16:42:00  QuestStartedEvent 1696        objectifs {10418: True}
            16:42:02  QuestObjectiveValidatedEvent  objectifs {10418: False, 10560: True}

        Un objectif absent de la liste n'est pas encore revele, donc pas fait non plus.
        """
        objective = self._find_objective(quest_id, objective_id)
        return objective is not None and not objective.objective_reached

    def _find_objective(self, quest_id: int, objective_id: int) -> QuestObjective | None:
        quest = self.active_quest_by_id.get(quest_id)
        if quest is None:
            return None
        return next(
            (objective for objective in quest.details.objectives if objective.objective_id == objective_id),
            None,
        )

    def reached_objective_ids(self, quest_id: int) -> set[int]:
        quest = self.active_quest_by_id.get(quest_id)
        if quest is None:
            return set()
        return {
            objective.objective_id
            for objective in quest.details.objectives
            if not objective.objective_reached
        }

    def known_objective_ids(self, quest_id: int) -> set[int]:
        quest = self.active_quest_by_id.get(quest_id)
        if quest is None:
            return set()
        return {objective.objective_id for objective in quest.details.objectives}

    def mark_objective_reached(self, quest_id: int, objective_id: int) -> None:
        objective = self._find_objective(quest_id, objective_id)
        if objective is not None:
            objective.objective_reached = False

    def is_finished(self, quest_id: int) -> bool:
        return self.finished_count_by_quest_id.get(quest_id, 0) > 0
