"""
Constantes du monde de Dofus (immuables).
Valeurs fixes provenant du jeu : map IDs, NPC IDs, skill IDs, etc.

⚠️ Ces valeurs NE DOIVENT PAS être modifiées par l'utilisateur.
Elles représentent des données fixes du jeu Dofus.

Pour configurer le comportement du bot, voir src/core/config.py
"""

from D3Database.enums.npc_message_id_enum import NpcAskMessageIdEnum
from D3Database.models.world_graph import Transition, Vertice
from src.core.engine.dungeons.dungeon_info import DungeonInfo
from src.core.engine.npcs.npc_dialog_info import ReplyInfo
from src.core.engine.npcs.npc_info import NpcInfo

# ============================================================================
# MAPS
# ============================================================================


class Maps:
    """Map IDs importantes du jeu"""

    # Banques
    ASTRUB_BANK = 192415750
    BONTA_BANK = 217059328
    BANKS = [ASTRUB_BANK, BONTA_BANK]

    # Hôtels de vente
    ASTRUB_SALE_HOTEL_COM = 191102976
    ASTRUB_SALE_HOTEL_RES = 191104004
    BONTA_SALE_HOTEL_COM = 212600839
    BONTA_SALE_HOTEL_RES = 212601350

    # Maps interdites pour pathfinding
    FORBIDDEN = {
        99096071,  # (3,-17)
        206046725,  # (1,-5)
        193331717,  # (4,2)
        99096067,  # (-16,4)
        103547392,  # (9,-17)
        153358342,  # (15,-31)
        153357312,  # (9,21)
        73400323,  # (4,-4)
    }


# ============================================================================
# NPCs
# ============================================================================


class NPCs:
    """NPCs importants et leurs actions"""

    # Banques
    ASTRUB_BANK = NpcInfo(
        npc_id=-20001,
        npc_map_id=Maps.ASTRUB_BANK,
        reply_info_by_message_id={
            NpcAskMessageIdEnum.ASTRUB_BANK_NPC_ASK_OPEN_CHEST: ReplyInfo(
                reply_id=64361, do_finish_after=True
            )
        },
    )
    BONTA_BANK = NpcInfo(
        npc_id=-20000,
        npc_map_id=Maps.BONTA_BANK,
        reply_info_by_message_id={
            NpcAskMessageIdEnum.BONTA_BANK_NPC_ASK_OPEN_CHEST: ReplyInfo(
                reply_id=63535, do_finish_after=True
            )
        },
    )
    BANKS = [ASTRUB_BANK, BONTA_BANK]

    # Hôtels de vente
    ASTRUB_SALE_HOTEL_COM_SELL = NpcInfo(
        npc_id=-1, npc_action_id=5, npc_map_id=Maps.ASTRUB_SALE_HOTEL_COM
    )
    ASTRUB_SALE_HOTEL_RES_SELL = NpcInfo(
        npc_id=-1, npc_action_id=5, npc_map_id=Maps.ASTRUB_SALE_HOTEL_RES
    )
    BONTA_SALE_HOTEL_COM_SELL = NpcInfo(
        npc_id=-1, npc_action_id=5, npc_map_id=Maps.BONTA_SALE_HOTEL_COM
    )
    BONTA_SALE_HOTEL_RES_SELL = NpcInfo(
        npc_id=-1, npc_action_id=5, npc_map_id=Maps.BONTA_SALE_HOTEL_RES
    )


# ============================================================================
# MONSTERS
# ============================================================================


class Monsters:
    """Races et monstres"""

    PROTECTOR_RACES = [
        66,  # protecteur alchimiste
        65,  # protecteur pecheur
        64,  # protecteur bucheron
        63,  # protecteur mineur
        62,  # protecteur paysan
    ]


# ============================================================================
# ITEMS
# ============================================================================


class Items:
    """Items et équipements fixes"""

    # Items spéciaux
    KEY_RING = 10207  # trousseau de clé
    INVENTORY_EQUIPMENT_POSITION = 63  # inventaire

    # custom mapping
    CUSTOM_GATHERER_BY_SAC = {
        7989: 1794,  # sac de carpe, carpe d'iem
        7993: 1784,  # sac de raies, raie bleue
        11112: 11107,  # sac de tremble, bois de tremble
    }


# ============================================================================
# SKILLS & CRAFTING
# ============================================================================


class Skills:
    """Skills et leurs maps associées"""

    # Map ID par Skill ID (pour le craft)
    MAP_BY_SKILL: dict[int, set[int]] = {
        101: {217063430, 192940034},  # scier (bucheron)
        23: {217057284, 192937988},  # preparer une potion (alchimiste)
        48: {217061380, 192939010},  # polir une pierre (mineur)
        32: {217060356, 192939010},  # fondre (mineur)
        47: {217061382, 192939008},  # moudre (paysan)
        27: {217061382, 192939008},  # cuire (paysan)
        135: {217062406, 192937984},  # preparer un poisson (pecheur)
        134: {192937994},  # preparer une viande (chasseur)
    }


# ============================================================================
# WAYPOINTS
# ============================================================================


class Waypoints:
    """Waypoint IDs (zaaps)"""

    FRIGOST = 54172969
    PANDALA = 207619076


# ============================================================================
# DUNGEONS
# ============================================================================


class Dungeons:
    """Informations sur les donjons"""

    GRANGE_TOURNESOL = DungeonInfo(name="Tournesol Affamé", key_name="Clef des Champs")
    BOUFTOU_ROYAL = DungeonInfo(name="Bouftou Royal", key_name="Cour du Bouftou Royal")
    ALL = [GRANGE_TOURNESOL, BOUFTOU_ROYAL]


# ============================================================================
# PATHFINDING
# ============================================================================


class PathfindingConst:
    """Constantes pour le pathfinding"""

    FORBIDDEN_EDGE_TRANSITION: set[tuple[Vertice, Vertice, Transition]] = set()
    EXCLUDED_ELEMENT_IDS: set[int] = set()
