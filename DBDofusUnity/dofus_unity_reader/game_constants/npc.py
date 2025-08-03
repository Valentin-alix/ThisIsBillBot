from enum import IntEnum

from pydantic import BaseModel

from dofus_unity_reader.game_constants.map_id import MapIdEnum


class ReplyInfo(BaseModel):
    reply_id: int
    do_finish_after: bool = False


class NpcDialogInfo:
    def __init__(
        self,
        npc_id: int | None = None,
        bones_id: int | None = None,
        cell_id: int | None = None,
        npc_action_id: int = 3,
        reply_info_by_message_id: dict[int, ReplyInfo] | None = None,
        forbidden_action_ids: list[int] | None = None,
    ) -> None:
        self.npc_id = npc_id
        self.bones_id = bones_id
        self.cell_id = cell_id
        self.npc_action_id = npc_action_id
        self.reply_info_by_message_id = reply_info_by_message_id or {}
        self.forbidden_action_ids = forbidden_action_ids or []


class NpcInfo(NpcDialogInfo):
    def __init__(
        self,
        npc_map_id: int,
        npc_id: int | None = None,
        bones_id: int | None = None,
        cell_id: int | None = None,
        npc_action_id: int = 3,
        reply_info_by_message_id: dict[int, ReplyInfo] | None = None,
        forbidden_action_ids: list[int] | None = None,
    ) -> None:
        super().__init__(
            npc_id=npc_id,
            bones_id=bones_id,
            cell_id=cell_id,
            npc_action_id=npc_action_id,
            reply_info_by_message_id=reply_info_by_message_id,
            forbidden_action_ids=forbidden_action_ids,
        )
        self.npc_map_id = npc_map_id


class NpcAskMessageIdEnum(IntEnum):
    ASTRUB_BANK_NPC_ASK_OPEN_CHEST = 48366
    BONTA_BANK_NPC_ASK_OPEN_CHEST = 47810
    HESITATE_BEFORE_GO_ANKARNOOB = 30637
    CONFIRM_GO_ASTRUB = 30639


ASTRUB_BANK_NPC = NpcInfo(
    npc_id=-20001,
    npc_map_id=MapIdEnum.ASTRUB_BANK,
    reply_info_by_message_id={
        NpcAskMessageIdEnum.ASTRUB_BANK_NPC_ASK_OPEN_CHEST: ReplyInfo(reply_id=64361, do_finish_after=True)
    },
)
BONTA_BANK_NPC = NpcInfo(
    npc_id=-20000,
    npc_map_id=MapIdEnum.BONTA_BANK,
    reply_info_by_message_id={
        NpcAskMessageIdEnum.BONTA_BANK_NPC_ASK_OPEN_CHEST: ReplyInfo(reply_id=63535, do_finish_after=True)
    },
)
BANK_NPCS = [ASTRUB_BANK_NPC, BONTA_BANK_NPC]

ASTRUB_SALE_HOTEL_COM_SELL_NPC = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=MapIdEnum.ASTRUB_SALE_HOTEL_COM
)
ASTRUB_SALE_HOTEL_RES_SELL_NPC = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=MapIdEnum.ASTRUB_SALE_HOTEL_RES
)
ASTRUB_SALE_HOTEL_EQUIPMENT_BUY_NPC = NpcInfo(npc_map_id=MapIdEnum.ASTRUB_SALE_HOTEL_EQUIP)
BONTA_SALE_HOTEL_COM_SELL_NPC = NpcInfo(npc_id=-1, npc_action_id=5, npc_map_id=MapIdEnum.BONTA_SALE_HOTEL_COM)
BONTA_SALE_HOTEL_RES_SELL_NPC = NpcInfo(npc_id=-1, npc_action_id=5, npc_map_id=MapIdEnum.BONTA_SALE_HOTEL_RES)
BONTA_SALE_HOTEL_EQUIP_SELL_NPC = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=MapIdEnum.BONTA_SALE_HOTEL_EQUIP
)
