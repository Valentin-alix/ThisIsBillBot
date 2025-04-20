from src.core.engine.items.set_infos.chance import CHANCE_SETS
from src.core.engine.items.set_infos.intelligence import INTELLIGENCE_SETS
from src.core.engine.items.set_infos.set_info import SetOnLevel

SET_BY_LEVEL_THRESHOLD = [
    CHANCE_SETS[0],
    INTELLIGENCE_SETS[0],
    CHANCE_SETS[1],
    INTELLIGENCE_SETS[1],
    INTELLIGENCE_SETS[2],
    CHANCE_SETS[2],
]

__all__ = ["SET_BY_LEVEL_THRESHOLD", "SetOnLevel"]
