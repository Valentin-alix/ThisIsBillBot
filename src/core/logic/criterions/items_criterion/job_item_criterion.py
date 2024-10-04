from src.core.logic.criterions.item_criterion import ItemCriterion


class JobItemCriterion(ItemCriterion):

    VALUE_NOT_SPECIFIC_JOB: int = 4.294967295e9

    _job_id: int

    _jobs_count: int

    _job_level: int = -1

    def __init__(self, p_criterion: str):
        is_validfloat: bool = False
        _job_identifier: list = None
        super().__init__(p_criterion)
        arrayParams: list = str(self.criterion_value_text).split(",")
        if arrayParams and len(arrayParams) > 0:
            if len(arrayParams) <= 2:
                is_validfloat = (int(arrayParams[0])) is not None and int(
                    arrayParams[0]
                ) > 0
                if is_validfloat:
                    self._job_id = int(arrayParams[0])
                    self._jobs_count = 1
                else:
                    _job_identifier = arrayParams[0].split("")
                    if _job_identifier[0] == "a":
                        self._job_id = self.VALUE_NOT_SPECIFIC_JOB
                        self._jobs_count = 1
                    elif _job_identifier[0] == "n":
                        self._job_id = self.VALUE_NOT_SPECIFIC_JOB
                        self._jobs_count = int(_job_identifier[1])
                    else:
                        self._job_id = 0
                        self._jobs_count = 0
                self._job_level = int(arrayParams[1])
        else:
            self._job_id = int(self.criterion_value)
            self._job_level = -1

    def is_respected(self, *args, **kwargs) -> bool:
        known_job: known_job_wrapper = None
        known_job_count: int = 0
        knownJobs: list = PlayedCharacterManager().jobs
        if self._jobs_count > 0:
            if self._job_id == self.VALUE_NOT_SPECIFIC_JOB:
                known_job_count = 0
                for known_job in knownJobs:
                    if known_job:
                        if (
                            self._job_level == -1
                            or known_job.jobLevel > self._job_level
                        ):
                            known_job_count += 1
                        if known_job_count >= self._jobs_count:
                            return True
            else:
                known_job = knownJobs[self._job_id]
                if not known_job:
                    return False
                if self._job_level == -1 or known_job.jobLevel > self._job_level:
                    return True
        return False
