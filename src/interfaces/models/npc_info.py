from dataclasses import dataclass


@dataclass
class NpcGenericAction:
    npc_id: int
    npc_action_id: int
    npc_map_id: int


@dataclass
class NpcInfo(NpcGenericAction):
    reply_ids: list[int]
