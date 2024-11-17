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
        99096071,
        206046725,
        193331717,
        99096067,
        103547392,
        153358342,
        153357312,
        73400323,
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

    PROTECTOR_RACES = [66, 65, 64, 63, 62]


# ============================================================================
# ITEMS
# ============================================================================


class Items:
    """Items et équipements fixes"""

    # Items spéciaux
    KEY_RING = 10207
    INVENTORY_EQUIPMENT_POSITION = 63

    # Mappings customs
    CUSTOM_GATHERER_BY_SAC = {7989: 1794, 7993: 1784, 11112: 11107}


# ============================================================================
# SKILLS & CRAFTING
# ============================================================================


class Skills:
    """Skills et leurs maps associées"""

    # Map ID par Skill ID (pour le craft)
    MAP_BY_SKILL: dict[int, set[int]] = {
        101: {217063430, 192940034},
        23: {217057284, 192937988},
        48: {217061380, 192939010},
        32: {217060356, 192939010},
        47: {217061382, 192939008},
        27: {217061382, 192939008},
        135: {217062406, 192937984},
        134: {192937994},
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


class Pathfinding:
    """Constantes pour le pathfinding"""

    FORBIDDEN_EDGE_TRANSITION: set[tuple[Vertice, Vertice, Transition]] = set()
    EXCLUDED_ELEMENT_IDS: set[int] = set()


# RÉTRO-COMPATIBILITÉ (deprecated, à supprimer progressivement)
# ============================================================================
# Ces alias permettent une migration en douceur du code existant

# Maps (deprecated)
ASTRUB_BANK_MAP = Maps.ASTRUB_BANK
BONTA_BANK_MAP = Maps.BONTA_BANK
BANK_MAP_IDS = Maps.BANKS
FORBIDDEN_MAP_IDS = Maps.FORBIDDEN

# NPCs (deprecated)
ASTRUB_BANK_NPC_INFO = NPCs.ASTRUB_BANK
BONTA_BANK_NPC_INFO = NPCs.BONTA_BANK
BANKS_NPC_INFOS = NPCs.BANKS
ASTRUB_SALE_HOTEL_COM_SELL_ACTION = NPCs.ASTRUB_SALE_HOTEL_COM_SELL
ASTRUB_SALE_HOTEL_RES_SELL_ACTION = NPCs.ASTRUB_SALE_HOTEL_RES_SELL
BONTA_SALE_HOTEL_COM_SELL_ACTION = NPCs.BONTA_SALE_HOTEL_COM_SELL
BONTA_SALE_HOTEL_RES_SELL_ACTION = NPCs.BONTA_SALE_HOTEL_RES_SELL

# Monsters (deprecated)
PROTECTOR_RACES = Monsters.PROTECTOR_RACES

# Items (deprecated)
KEY_RING_ITEM_ID = Items.KEY_RING
INVENTORY_EQUIPMENT_POSITION = Items.INVENTORY_EQUIPMENT_POSITION
CUSTOM_GATHERER_ITEM_BY_SAC_GID = Items.CUSTOM_GATHERER_BY_SAC

# Skills (deprecated)
MAP_ID_BY_SKILL_ID = Skills.MAP_BY_SKILL

# Dungeons (deprecated)
GRANGE_TOURNESOL = Dungeons.GRANGE_TOURNESOL
BOUFTOU_ROYAL = Dungeons.BOUFTOU_ROYAL
DUNGEONS_INFOS = Dungeons.ALL

# Pathfinding (deprecated)
FORBIDDEN_EDGE_TRANSITION = Pathfinding.FORBIDDEN_EDGE_TRANSITION
EXCLUDED_ELEMENT_IDS = Pathfinding.EXCLUDED_ELEMENT_IDS
