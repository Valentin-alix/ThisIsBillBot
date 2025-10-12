from DBDofusUnity.dofus_unity_reader.game_constants.item import ItemEnum
from DBDofusUnity.dofus_unity_reader.game_constants.map_id import MapIdEnum
from DBDofusUnity.dofus_unity_reader.game_constants.quest import (
    QuestEnum,
    QuestObjectiveEnum,
    QuestStepEnum,
)

from src.core.engine.npcs.dialog_turn import DialogTurn
from src.core.engine.npcs.reply_selector import ByText
from src.core.engine.quests.quest_script import (
    BuyItemStep,
    CraftItemStep,
    QuestCooldown,
    QuestScript,
    QuestStep,
    TalkToNpcStep,
    UseMapInteractiveStep,
)

MAX_KAMAS_PER_INGREDIENT = 5_000
MAX_KAMAS_POILS_DE_KERUBIM = 50_000


def _polish_furniture(map_id: MapIdEnum) -> UseMapInteractiveStep:
    return UseMapInteractiveStep(map_ids={map_id})


_STEPS: list[QuestStep] = [
    TalkToNpcStep(
        map_ids={MapIdEnum.KERUBIM_SHOP},
        npc_name="Kerubim Crepin",
        turns=[
            DialogTurn(reply=ByText(pattern=r"odeur bizarre dans la piece")),
            DialogTurn(reply=ByText(pattern=r"proposer une nouvelle fois votre aide")),
            DialogTurn(reply=ByText(pattern=r"proposer votre aide pour trouver de la cire")),
            DialogTurn(reply=ByText(pattern=r"partir se procurer les ingredients")),
        ],
    ),
    BuyItemStep(
        item_gid=ItemEnum.GRAISSE_GELATINEUSE,
        max_kamas=MAX_KAMAS_PER_INGREDIENT,
        quantity=5,
    ),
    BuyItemStep(
        item_gid=ItemEnum.GROIN_DE_SANGLIER_DES_PLAINES,
        max_kamas=MAX_KAMAS_PER_INGREDIENT,
        quantity=2,
    ),
    BuyItemStep(
        item_gid=ItemEnum.DEFENSE_DU_SANGLIER,
        max_kamas=MAX_KAMAS_PER_INGREDIENT,
        quantity=2,
    ),
    BuyItemStep(
        item_gid=ItemEnum.POILS_DE_KERUBIM,
        max_kamas=MAX_KAMAS_POILS_DE_KERUBIM,
    ),
    CraftItemStep(item_gid=ItemEnum.CIRE_DE_GLIGLI),
    _polish_furniture(MapIdEnum.KERUBIM_SHOP_ENTRANCE),
    _polish_furniture(MapIdEnum.KERUBIM_SHOP_ENTRANCE),
    _polish_furniture(MapIdEnum.KERUBIM_SHOP_ENTRANCE),
    _polish_furniture(MapIdEnum.KERUBIM_SHOP),
    _polish_furniture(MapIdEnum.KERUBIM_SHOP),
    TalkToNpcStep(
        map_ids={MapIdEnum.KERUBIM_SHOP},
        npc_name="Kerubim Crepin",
        turns=[
            DialogTurn(reply=ByText(pattern=r"termine d'astiquer les meubles")),
            DialogTurn(reply=ByText(pattern=r"titre de nettoyeur de shushu")),
            DialogTurn(reply=ByText(pattern=r"le remercier et s'en aller")),
        ],
    ),
]

IL_FAUT_QUE_CHA_BRILLE = QuestScript(
    name="Il faut que cha brille",
    quest_id=QuestEnum.IL_FAUT_QUE_CHA_BRILLE,
    cooldown=QuestCooldown.WEEKLY,
    level_min=15,
    steps=_STEPS,
    server_step_id_by_index={0: QuestStepEnum.IL_FAUT_QUE_CHA_BRILLE},
    objective_id_by_index={
        1: QuestObjectiveEnum.CHA_BRILLE_FABRIQUER_CIRE,
        2: QuestObjectiveEnum.CHA_BRILLE_FABRIQUER_CIRE,
        3: QuestObjectiveEnum.CHA_BRILLE_FABRIQUER_CIRE,
        4: QuestObjectiveEnum.CHA_BRILLE_FABRIQUER_CIRE,
        5: QuestObjectiveEnum.CHA_BRILLE_FABRIQUER_CIRE,
        6: QuestObjectiveEnum.CHA_BRILLE_PETITE_COMMODE,
        7: QuestObjectiveEnum.CHA_BRILLE_GRANDE_COMMODE,
        8: QuestObjectiveEnum.CHA_BRILLE_OEIL_DE_LUIS,
        9: QuestObjectiveEnum.CHA_BRILLE_ETAGERE_HAUT_1,
        10: QuestObjectiveEnum.CHA_BRILLE_ETAGERE_HAUT_2,
        11: QuestObjectiveEnum.CHA_BRILLE_RENDRE_COMPTE,
    },
    objective_ids_with_untrusted_map={
        QuestObjectiveEnum.CHA_BRILLE_ETAGERE_HAUT_1,
        QuestObjectiveEnum.CHA_BRILLE_ETAGERE_HAUT_2,
    },
)
