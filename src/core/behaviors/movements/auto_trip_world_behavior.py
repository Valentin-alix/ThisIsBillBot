from dataclasses import dataclass

from db_dofus_unity.protos.game.gamemap_pb2 import MapComplementaryInformationEvent
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip_zaap_behavior import AutoTripZaapBehavior
from src.core.behaviors.npc_dialog_behavior import NpcInfo, NpcDialogBehavior
from src.core.repositories.data_reader import DataReader
from src.core.states.map_state import MapState
from src.interfaces.enums.world import WorldEnum

NPC_PORTAL_INCARNAM = NpcInfo(
    npc_map_id=153880835,
    npc_action_id=3,
    npc_id=-20001,
    reply_ids=[36982, 36980],
)


@dataclass
class AutoTripWorldBehavior(Behavior):
    auto_trip_zaap_behavior: AutoTripZaapBehavior
    map_state: MapState
    npc_dialog_behavior: NpcDialogBehavior

    def run(self, dst: set[int]) -> None:
        """auto trip to either one of map ids or edge"""
        from_map_data = DataReader().map_pos_by_map_id[self.map_state.map_id]
        to_map_data = DataReader().map_pos_by_map_id[next(iter(dst))]

        from_world = WorldEnum(from_map_data.worldMap)
        dst_world = WorldEnum(to_map_data.worldMap)
        if from_world != dst_world:
            self.from_incarnam_go_astrub(dst)
        else:
            self.auto_trip_zaap_behavior.start(
                callback=self.finish, parent=self, dst=dst
            )

    def from_incarnam_go_astrub(self, dst: set[int]):
        def on_npc_map():
            self.event_manager.on(
                MapComplementaryInformationEvent,
                callback=lambda _: self.auto_trip_zaap_behavior.start(
                    callback=self.finish, parent=self, dst=dst
                ),
                originator=self,
                once=True,
            )
            self.npc_dialog_behavior.start(
                callback=None,
                parent=self,
                npc_info=NPC_PORTAL_INCARNAM,
            )

        self.auto_trip_zaap_behavior.start(
            callback=lambda _: on_npc_map(),
            parent=self,
            dst={NPC_PORTAL_INCARNAM.npc_map_id},
        )
