from dataclasses import dataclass

from src.core.engine.npcs.npc_dialog_info import NpcDialogInfo


@dataclass(kw_only=True)
class NpcInfo(NpcDialogInfo):
    npc_map_id: int
