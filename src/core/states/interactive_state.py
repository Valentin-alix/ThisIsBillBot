from dataclasses import dataclass, field

from com.ankama.dofus.server.game.protocol.common_pb2 import InteractiveElement
from src.core.logic.farmer.consts import HARVESTER_JOB_NAMES
from src.core.repositories.data_reader import DataReader
from src.core.repositories.i18n import I18N
from src.core.states.player_state import PlayerState
from src.core.states.state import State


@dataclass
class InteractiveElementInfo:
    state: int
    interactive_element: InteractiveElement

    def is_interactive_selectable(self):
        return self.interactive_element.on_current_map and self.state == 0


@dataclass
class Collectable:
    interactive_element: InteractiveElementInfo
    skill: InteractiveElement.InteractiveElementSkill

    def is_farmable(self, job_lvl: int) -> bool:
        related_skill_data = DataReader().skill_by_id[self.skill.skill_id]
        if related_skill_data.levelMin > job_lvl:
            return False
        related_job = related_skill_data.parentJobId
        related_job_name_id = DataReader().job_by_id[related_job].nameId
        related_job_name = I18N().name_by_id[related_job_name_id]
        return related_job_name in HARVESTER_JOB_NAMES


@dataclass
class InteractiveState(State):
    player_state: PlayerState
    interactive_elements_by_id: dict[int, InteractiveElementInfo] = field(
        init=False, default_factory=lambda: {}
    )

    def get_farmable_collectables(self) -> list[Collectable]:
        farmable_collectables: list[Collectable] = []
        for interactive_element_info in self.interactive_elements_by_id.values():
            if not interactive_element_info.is_interactive_selectable():
                continue
            if len(interactive_element_info.interactive_element.enabled_skills) == 0:
                continue
            skill = interactive_element_info.interactive_element.enabled_skills[0]
            collectable = Collectable(
                interactive_element=interactive_element_info,
                skill=skill,
            )
            if collectable.is_farmable(0):  # TODO
                farmable_collectables.append(collectable)

        return farmable_collectables
