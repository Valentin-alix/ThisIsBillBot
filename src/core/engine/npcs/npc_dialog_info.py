from dataclasses import dataclass, field


@dataclass
class NpcDialogInfo:
    npc_id: int
    npc_action_id: int = 3
    include_reply_ids: list[int] | None = field(default=None)
    exclude_reply_ids: list[int] = field(default_factory=list)
    exclude_action_ids: list[int] = field(default_factory=list)
