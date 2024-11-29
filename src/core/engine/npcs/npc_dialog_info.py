from pydantic import BaseModel


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
