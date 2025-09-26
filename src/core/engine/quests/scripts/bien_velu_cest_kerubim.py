from dofus_unity_reader.game_constants.map_id import MapIdEnum
from dofus_unity_reader.game_constants.quest import (
    QuestEnum,
    QuestObjectiveEnum,
    QuestStepEnum,
)

from src.core.engine.npcs.dialog_turn import DialogTurn
from src.core.engine.npcs.reply_selector import ByText
from src.core.engine.quests.quest_script import (
    QuestCooldown,
    QuestScript,
    QuestStep,
    TalkToNpcStep,
)


def _talk_to_kerubim(turn_variants: list[list[DialogTurn]]) -> TalkToNpcStep:
    return TalkToNpcStep(
        map_ids={MapIdEnum.KERUBIM_SHOP},
        npc_name="Kerubim Crepin",
        turn_variants=turn_variants,
    )


_STEPS: list[QuestStep] = [
    _talk_to_kerubim(
        [
            [
                DialogTurn(reply=ByText(pattern=r"objets legendaires")),
                DialogTurn(reply=ByText(pattern=r"cet ingrédient")),
                DialogTurn(reply=ByText(pattern=r"demander ce que c'est")),
                DialogTurn(reply=ByText(pattern=r"le rassurer et l'interroger")),
                DialogTurn(reply=ByText(pattern=r"en savoir plus a ce sujet")),
                DialogTurn(reply=ByText(pattern=r"ecouter sa proposition")),
                DialogTurn(reply=ByText(pattern=r"^accepter\.$"), finish_after=True),
            ],
            [
                DialogTurn(reply=ByText(pattern=r"une autre dose de l'ingrédient")),
                DialogTurn(
                    reply=ByText(pattern=r"partir à la recherche des xelors"),
                    finish_after=True,
                ),
            ],
        ]
    ),
    TalkToNpcStep(
        coord=(6, -16), npc_name="Xelor Louche", turns=[DialogTurn(reply=ByText(pattern=r"mettre fin"))]
    ),
    TalkToNpcStep(
        coord=(-3, -24),
        npc_name="Xelor Interlope",
        turns=[DialogTurn(reply=ByText(pattern=r"comme un milirat"))],
    ),
    TalkToNpcStep(
        coord=(3, 1), npc_name="Xelor Suspect", turns=[DialogTurn(reply=ByText(pattern=r"violence"))]
    ),
    _talk_to_kerubim([[DialogTurn(reply=ByText(pattern=r"caisses du xelor"), finish_after=True)]]),
]

BIEN_VELU_CEST_KERUBIM = QuestScript(
    name="Bien velu, c'est Kerubim",
    quest_id=QuestEnum.BIEN_VELU_CEST_KERUBIM,
    cooldown=QuestCooldown.DAILY,
    level_min=15,
    steps=_STEPS,
    server_step_id_by_index={0: QuestStepEnum.BIEN_VELU_CEST_KERUBIM},
    objective_id_by_index={
        1: QuestObjectiveEnum.BIEN_VELU_XELOR_LOUCHE,
        2: QuestObjectiveEnum.BIEN_VELU_XELOR_INTERLOPE,
        3: QuestObjectiveEnum.BIEN_VELU_XELOR_SUSPECT,
        4: QuestObjectiveEnum.BIEN_VELU_RENDRE_CAISSES,
    },
)
