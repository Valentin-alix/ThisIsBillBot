from enum import IntEnum

from DBDofusUnity.dofus_unity_reader.game_constants.map_id import MapIdEnum
from pydantic import BaseModel


class ReplyInfo(BaseModel):
    reply_id: int
    do_finish_after: bool = False


class NpcActionEnum(IntEnum):
    BUY_SELL = 1
    TALK = 3
    SELL = 5
    BUY = 6


class NpcDialogInfo:
    def __init__(
        self,
        npc_name: str | None = None,
        npc_id: int | None = None,
        bones_id: int | None = None,
        cell_id: int | None = None,
        npc_action_id: int = NpcActionEnum.TALK,
    ) -> None:
        self.npc_name = npc_name
        self.npc_id = npc_id
        self.bones_id = bones_id
        self.cell_id = cell_id
        self.npc_action_id = npc_action_id


class NpcInfo(NpcDialogInfo):
    def __init__(
        self,
        npc_map_id: int,
        npc_name: str | None = None,
        npc_id: int | None = None,
        bones_id: int | None = None,
        cell_id: int | None = None,
        npc_action_id: int = NpcActionEnum.TALK,
    ) -> None:
        super().__init__(
            npc_name=npc_name,
            npc_id=npc_id,
            bones_id=bones_id,
            cell_id=cell_id,
            npc_action_id=npc_action_id,
        )
        self.npc_map_id = npc_map_id


class NpcAskMessageIdEnum(IntEnum):
    ASTRUB_BANK_NPC_ASK_OPEN_CHEST = 13403


ASTRUB_BANK_NPC = NpcInfo(npc_name="Al Etsop", npc_map_id=MapIdEnum.ASTRUB_BANK)
BONTA_BANK_NPC = NpcInfo(npc_name="Banquier bontarien", npc_map_id=MapIdEnum.BONTA_BANK)
BANK_NPCS = [ASTRUB_BANK_NPC, BONTA_BANK_NPC]

# npc_id=-1 designe l'interface HDV, qui n'a pas de PNJ nomme.
SALE_HOTEL_NPC_ID = -1

ASTRUB_SALE_HOTEL_COM_SELL_NPC = NpcInfo(
    npc_id=SALE_HOTEL_NPC_ID,
    npc_action_id=NpcActionEnum.SELL,
    npc_map_id=MapIdEnum.ASTRUB_SALE_HOTEL_COM,
)
ASTRUB_SALE_HOTEL_RES_SELL_NPC = NpcInfo(
    npc_id=SALE_HOTEL_NPC_ID,
    npc_action_id=NpcActionEnum.SELL,
    npc_map_id=MapIdEnum.ASTRUB_SALE_HOTEL_RES,
)
ASTRUB_SALE_HOTEL_EQUIPMENT_BUY_NPC = NpcInfo(npc_map_id=MapIdEnum.ASTRUB_SALE_HOTEL_EQUIP)
BONTA_SALE_HOTEL_COM_SELL_NPC = NpcInfo(
    npc_id=SALE_HOTEL_NPC_ID,
    npc_action_id=NpcActionEnum.SELL,
    npc_map_id=MapIdEnum.BONTA_SALE_HOTEL_COM,
)
BONTA_SALE_HOTEL_RES_SELL_NPC = NpcInfo(
    npc_id=SALE_HOTEL_NPC_ID,
    npc_action_id=NpcActionEnum.SELL,
    npc_map_id=MapIdEnum.BONTA_SALE_HOTEL_RES,
)
BONTA_SALE_HOTEL_EQUIP_SELL_NPC = NpcInfo(
    npc_id=SALE_HOTEL_NPC_ID,
    npc_action_id=NpcActionEnum.SELL,
    npc_map_id=MapIdEnum.BONTA_SALE_HOTEL_EQUIP,
)
