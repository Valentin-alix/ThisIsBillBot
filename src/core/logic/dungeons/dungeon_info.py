from data_center.data_reader import DataReader
from data_center.i18n import I18N
from src.interfaces.models.npc_info import NpcDialogInfo, NpcInfo


class DungeonInfo:
    def __init__(
        self,
        name: str,
        key_name: str,
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
            npc_id=-20000,
            npc_map_id=self.dungeon.entranceMapId,
            exclude_action_ids=[1074],
        )
        self.exit_npc_info = NpcDialogInfo(npc_id=-20000)

    def __post_init__(self):
        self.dungeon = DataReader().dungeon_by_entrance_map_id[
            self.entrance_npc_info.npc_map_id
        ]
