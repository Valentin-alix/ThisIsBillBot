from dataclasses import dataclass

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.map_reader import MapReader
from D3Database.enums.jobs_enum import HARVESTER_JOB_IDS
from D3Database.grid.map_point import MapPoint
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    InteractiveElement,
    StatedElement,
)


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
            .get_ref_data_by_element_id_by_map_id(self.map_id)[
                self.interactive_element.element_id
            ]
            .cellId
        )
        if cell_id is None:
            raise ValueError("Player can't stand on a cell that have no id !")
        return MapPoint.from_cell_id(cell_id)


def get_stated_element_collectable(
    stated_element: StatedElement,
    interactive_element_by_id: dict[int, InteractiveElement],
    map_id: int,
    jobs_lvl_by_id: dict[int, int],
) -> Collectable | None:
    """
    Derive a Collectable from a StatedElement if it represents a valid farmable resource.

    Args:
        stated_element: The StatedElement to analyze
        interactive_element_by_id: Dictionary of element_id -> InteractiveElement
        map_id: Current map ID
        jobs_lvl_by_id: Dictionary of job_id -> job_level

    Returns:
        Collectable instance if valid farmable resource, None otherwise
    """
    # Filter out non-idle states
    if stated_element.state != 0:
        return None

    # Get the related interactive element
    related_interactive = interactive_element_by_id.get(stated_element.element_id)
    if (
        not related_interactive
        or related_interactive.on_current_map is not True
        or len(related_interactive.enabled_skills) == 0
    ):
        return None

    # Check if skill gathers a resource
    skill = related_interactive.enabled_skills[0]
    data_skill = DataReader().skill_by_id[skill.skill_id]
    if data_skill.gatheredRessourceItem in [-1, 0]:
        return None

    # Create collectable and validate farmability
    collectable = Collectable(
        map_id=map_id,
        interactive_element=related_interactive,
        skill=skill,
        resource_item_id=data_skill.gatheredRessourceItem,
    )

    # Check if player has sufficient job level
    player_job_level = jobs_lvl_by_id.get(data_skill.parentJobId, 1)
    if not collectable.is_farmable(player_job_level):
        return None

    return collectable
