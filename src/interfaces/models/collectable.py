from dataclasses import dataclass

from protos.game.common_pb2 import InteractiveElement
from src.core.data_center.data_reader import DataReader
from src.core.data_center.map_reader import MapReader
from src.core.logic.farmer.jobs import HARVESTER_JOB_IDS
from src.core.logic.grid.map_point import MapPoint


@dataclass
class Collectable:
    map_id: int
    interactive_element: InteractiveElement
    skill: InteractiveElement.InteractiveElementSkill
    resource_item_id: int

    def is_farmable(self, job_lvl: int) -> bool:
        related_skill_data = DataReader().skill_by_id[self.skill.skill_id]
        if related_skill_data.levelMin > job_lvl:
            return False
        related_job = related_skill_data.parentJobId
        return related_job in HARVESTER_JOB_IDS

    @property
    def mp(self) -> MapPoint:
        cell_id = (
            MapReader()
            .get_ref_data_by_element_id(self.map_id)[
                self.interactive_element.element_id
            ]
            .cellId
        )
        return MapPoint.from_cell_id(cell_id)
