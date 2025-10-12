"""Quete 1199 -- "Scene de menage", objectifs dans `quest_step_by_id[1816]`.

`repeatType=0` : non repetable, `QuestBehavior` la saute une fois validee.
"""

from DBDofusUnity.dofus_unity_reader.game_constants.map_id import MapIdEnum
from DBDofusUnity.dofus_unity_reader.game_constants.quest import (
    QuestEnum,
    QuestObjectiveEnum,
    QuestStepEnum,
)
from DBDofusUnity.dofus_unity_reader.game_constants.world import WorldMapEnum

from src.core.engine.npcs.dialog_turn import DialogTurn
from src.core.engine.npcs.reply_selector import ByText
from src.core.engine.quests.quest_script import (
    QuestCooldown,
    QuestScript,
    QuestStep,
    TalkToNpcStep,
    UseInteractiveStep,
)

MINE_ENTRANCE_COORD = (1, -17)
HERDEGRIZE_COORD = (7, -19)
SNORI_NAIRB_COORD = (4, -18)


_STEPS: list[QuestStep] = [
    TalkToNpcStep(
        map_ids={MapIdEnum.KERUBIM_SHOP},
        npc_name="Kerubim Crepin",
        turns=[
            DialogTurn(reply=ByText(pattern=r"milice des kerubims")),
            DialogTurn(reply=ByText(pattern=r"^continuer a ecouter\.$")),
            DialogTurn(reply=ByText(pattern=r"^ecouter la suite\.$")),
            DialogTurn(reply=ByText(pattern=r"^continuer a ecouter\.$")),
            DialogTurn(reply=ByText(pattern=r"^ecouter la suite\.$")),
            DialogTurn(reply=ByText(pattern=r"accepter de l'aider")),
            DialogTurn(reply=ByText(pattern=r"partir chercher les plumes")),
        ],
    ),
    TalkToNpcStep(
        coord=MINE_ENTRANCE_COORD,
        world=WorldMapEnum.UNDERGROUND,
        npc_name="Gaztronom",
        turns=[DialogTurn(reply=ByText(pattern=r"piquer une plume"))],
    ),
    TalkToNpcStep(
        coord=HERDEGRIZE_COORD,
        npc_name="Herdegrize",
        turns=[
            DialogTurn(reply=ByText(pattern=r"engager la conversation")),
            DialogTurn(reply=ByText(pattern=r"patienter tandis qu'herdegrize")),
            DialogTurn(reply=ByText(pattern=r"applaudir des deux mains")),
            DialogTurn(reply=ByText(pattern=r"souffler sur la page")),
        ],
    ),
    TalkToNpcStep(
        coord=HERDEGRIZE_COORD,
        npc_name="Herdegrize",
        turns=[
            DialogTurn(reply=ByText(pattern=r"lui demander une plume")),
            DialogTurn(reply=ByText(pattern=r"le flatter sans vergogne")),
            DialogTurn(reply=ByText(pattern=r"remercier vilement")),
        ],
    ),
    TalkToNpcStep(
        map_ids={MapIdEnum.ASTRUB_BANK},
        npc_name="Essiac d'Engrape",
        turns=[
            DialogTurn(reply=ByText(pattern=r"ici pour le plumer")),
            DialogTurn(reply=ByText(pattern=r"interroger snori nairb")),
        ],
    ),
    TalkToNpcStep(
        coord=SNORI_NAIRB_COORD,
        npc_name="Snori Nairb",
        turns=[
            DialogTurn(reply=ByText(pattern=r"a propos d'essiac")),
            DialogTurn(reply=ByText(pattern=r"ce qui s'est passe")),
            DialogTurn(reply=ByText(pattern=r"se rendre a la taverne")),
        ],
    ),
    UseInteractiveStep(map_ids={MapIdEnum.TAVERN_UPPER_FLOOR}, cell_id=261),
    TalkToNpcStep(
        map_ids={MapIdEnum.KERUBIM_SHOP},
        npc_name="Kerubim Crepin",
        turns=[DialogTurn(reply=ByText(pattern=r"donner les trois plumes"), finish_after=True)],
    ),
]

SCENE_DE_MENAGE = QuestScript(
    name="Scene de menage",
    quest_id=QuestEnum.SCENE_DE_MENAGE,
    cooldown=QuestCooldown.NONE,
    level_min=15,
    steps=_STEPS,
    server_step_id_by_index={0: QuestStepEnum.SCENE_DE_MENAGE},
    objective_id_by_index={
        1: QuestObjectiveEnum.MENAGE_PLUME_TOFU,
        2: QuestObjectiveEnum.MENAGE_PLUME_SCRIBOUILLARD,
        3: QuestObjectiveEnum.MENAGE_PLUME_SCRIBOUILLARD,
        4: QuestObjectiveEnum.MENAGE_BANQUIER,
        5: QuestObjectiveEnum.MENAGE_SNORI,
        6: QuestObjectiveEnum.MENAGE_PLUME_HIBOU,
        7: QuestObjectiveEnum.MENAGE_RENDRE_PLUMES,
    },
)
