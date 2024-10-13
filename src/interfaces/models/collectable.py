from dataclasses import dataclass

from d3_mapping.resources.protos.game.common_pb2 import InteractiveElement
from data_center.data_reader import DataReader
from data_center.map_reader import MapReader
from grid.map_point import MapPoint
from src.interfaces.enums.job_enum import HARVESTER_JOB_IDS


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
        if cell_id is None:
            raise ValueError("Player can't stand on a cell that have no id !")
        return MapPoint.from_cell_id(cell_id)
