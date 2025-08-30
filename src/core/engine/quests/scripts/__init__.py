"""Registry of quest scripts, mirroring `PLAYABLE_DUNGEONS`. See `docs/quests.md`."""

from src.core.engine.quests.quest_script import QuestScript
from src.core.engine.quests.scripts.bien_velu_cest_kerubim import BIEN_VELU_CEST_KERUBIM
from src.core.engine.quests.scripts.scene_de_menage import SCENE_DE_MENAGE

QUEST_SCRIPTS: list[QuestScript] = [SCENE_DE_MENAGE, BIEN_VELU_CEST_KERUBIM]
