from dataclasses import dataclass, field
from datetime import datetime

from DBDofusUnity.datas.protos.non_obf.connection.login_message_pb2 import SelectServerRequest
from DBDofusUnity.datas.protos.non_obf.game.character_management_pb2 import CharacterSelectionEvent
from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import CharacterLevelUpEvent
from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import ExchangeStartedWithMultiTabStorageEvent
from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent
from DBDofusUnity.datas.protos.non_obf.game.guild_member_pb2 import GuildMembershipEvent
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import InventoryContentEvent, KamasUpdateEvent
from DBDofusUnity.datas.protos.non_obf.game.job_pb2 import JobExperiencesUpdateEvent
from google.protobuf.message import Message

from src.controller.player_info_storage import PlayerInfoSnapshot, PlayerInfoStorage
from src.core.events_manager.priority import PriorityEnum
from src.core.frames.frame import Frame


@dataclass
class PlayerInfoSnapshotFrame(Frame):
    storage: PlayerInfoStorage = field(default_factory=PlayerInfoStorage)

    def __post_init__(self) -> None:
        self.priority = PriorityEnum.NORMAL
        for event_type in (
            CharacterSelectionEvent,
            CharacterLevelUpEvent,
            JobExperiencesUpdateEvent,
            InventoryContentEvent,
            KamasUpdateEvent,
            MapCurrentEvent,
            SelectServerRequest,
            ExchangeStartedWithMultiTabStorageEvent,
            GuildMembershipEvent,
        ):
            self.event_manager.on(
                event_type,
                self.record_snapshot_after_state_update,
                originator=self,
                priority=self.priority,
            )

    def record_snapshot_after_state_update(self, _: Message) -> None:
        player = self.game_state.player
        if player.character_id == 0:
            return
        self.storage.save_snapshot(
            player.login,
            PlayerInfoSnapshot(
                updated_at=datetime.now().astimezone(),
                character_id=player.character_id,
                character_name=player.character_name,
                breed_id=self.game_state.fight.breed_id,
                level=player.level,
                kamas=self.game_state.inventory.kamas,
                server_id=player.server_id,
                job_levels_by_id=dict(player.job_levels_by_id),
                map_id=self.game_state.map.map_id,
                has_guild=self.game_state.guild_chest.has_guild,
                guild_chest_tab_number=self.game_state.guild_chest.tab_number,
            ),
        )
