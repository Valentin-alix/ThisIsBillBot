from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)


class JobItemCriterion(ItemCriterion):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.jobs_count: int = 0
        self.job_id: int | None = None
        self.job_lvl = -1

        array_params: list[str] = str(self.criterion_value_text).split(",")
        if len(array_params) > 0:
            if len(array_params) <= 2:
                is_valid_float = (int(array_params[0])) is not None and int(array_params[0]) > 0
                if is_valid_float:
                    self.job_id = int(array_params[0])
                    self.jobs_count = 1
                else:
                    _job_identifier = array_params[0].split("")
                    if _job_identifier[0] == "a":
                        self.job_id = None
                        self.jobs_count = 1
                    elif _job_identifier[0] == "n":
                        self.job_id = None
                        self.jobs_count = int(_job_identifier[1])
                    else:
                        self.job_id = 0
                        self.jobs_count = 0
                self.job_lvl = int(array_params[1])
        else:
            self.job_id = int(self.criterion_value)
            self.job_lvl = -1

    def is_respected(self, context: CriterionContext) -> bool:
        if self.jobs_count > 0:
            if self.job_id is None:
                known_job_count = 0
                for player_job_lvl in context.player_jobs_lvl_by_id.values():
                    if self.job_lvl == -1 or player_job_lvl > self.job_lvl:
                        known_job_count += 1
                    if known_job_count >= self.jobs_count:
                        return True
            else:
                related_player_job_lvl = context.player_jobs_lvl_by_id.get(self.job_id)
                if related_player_job_lvl is None:
                    return False
                if self.job_lvl == -1 or related_player_job_lvl > self.job_lvl:
                    return True
        return False
