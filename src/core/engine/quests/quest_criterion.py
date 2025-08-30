import re
from functools import lru_cache

from dofus_unity_reader.data_center.data_reader import DataReader

_FINISHED_QUEST_TERM = re.compile(r"Qf=(\d+)")


def _split_top_level_and(criterion: str) -> list[str]:
    terms: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(criterion):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "&" and depth == 0:
            terms.append(criterion[start:index])
            start = index + 1
    terms.append(criterion[start:])
    return terms


@lru_cache(maxsize=256)
def get_required_finished_quest_ids(quest_id: int) -> frozenset[int]:
    quest = DataReader().quest_by_id.get(quest_id)
    if quest is None or not quest.startCriterion:
        return frozenset()
    return frozenset(
        int(match.group(1))
        for term in _split_top_level_and(quest.startCriterion)
        if (match := _FINISHED_QUEST_TERM.fullmatch(term)) is not None
    )
