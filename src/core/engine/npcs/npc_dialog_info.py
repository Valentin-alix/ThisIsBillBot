from dataclasses import dataclass, field

from pydantic import BaseModel


class ReplyInfo(BaseModel):
    reply_id: int
    do_finish_after: bool = False


@dataclass
class NpcDialogInfo:
    npc_id: int
    npc_action_id: int = 3

    reply_info_by_message_id: dict[int, ReplyInfo] = field(default_factory=dict)
    forbidden_action_ids: list[int] = field(default_factory=list)
