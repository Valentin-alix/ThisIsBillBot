from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from src.core.engine.npcs.npc_dialog_info import NpcDialogInfo
from src.core.engine.npcs.npc_info import NpcInfo


class DungeonInfo:
    def __init__(
        self,
        name: str,
        key_name: str,
        entrance_npc_id: int = -20000,
        exit_npc_id: int = -20000,
        entrance_bones_id: int | None = None,
        exit_bones_id: int | None = None,
    ) -> None:
        self.name = name
        self.key_name = key_name
        self.dungeon = next(
            dungeon
            for dungeon in DataReader().dungeon_by_id.values()
            if name.lower() in I18N().name_by_id[dungeon.nameId].lower()
            and len(dungeon.mapIds) > 2
        )
        self.entrance_npc_info = NpcInfo(
            npc_id=entrance_npc_id,
            bones_id=entrance_bones_id,
            npc_map_id=self.dungeon.entranceMapId,
            forbidden_action_ids=[1074],
        )
        self.exit_npc_info = NpcDialogInfo(npc_id=exit_npc_id, bones_id=exit_bones_id)

    def __post_init__(self):
        self.dungeon = DataReader().dungeon_by_entrance_map_id[
            self.entrance_npc_info.npc_map_id
        ]
