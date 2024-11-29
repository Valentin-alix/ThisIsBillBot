from src.core.engine.npcs.npc_dialog_info import NpcDialogInfo, ReplyInfo


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
