from dataclasses import dataclass

from db_dofus_unity.protos.game.common_pb2 import InteractiveElement
from src.core.logic.farmer.consts import HARVESTER_JOB_NAMES
from src.core.repositories.data_reader import DataReader
from src.core.repositories.i18n import I18N
from src.interfaces.models.interactive import InteractiveElementInfo


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
