from dataclasses import dataclass
from functools import partial

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.enums.area_enum import AreaEnum
from dofus_unity_reader.enums.npc_message_id_enum import NpcAskMessageIdEnum
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_explorator_behavior import (
    AutoTripExploratorBehavior,
)
from src.core.behaviors.npcs.npc_dialog_behavior import NpcDialogBehavior
from src.core.engine.npcs.npc_dialog_info import ReplyInfo
from src.core.engine.npcs.npc_info import NpcInfo

NPC_PORTAL_INCARNAM = NpcInfo(
    npc_map_id=153880835,
    npc_action_id=3,
    npc_id=-20001,
    reply_info_by_message_id={
        NpcAskMessageIdEnum.HESITATE_BEFORE_GO_ANKARNOOB: ReplyInfo(reply_id=36982),
        NpcAskMessageIdEnum.CONFIRM_GO_ASTRUB: ReplyInfo(
            reply_id=36980, do_finish_after=True
        ),
    },
)


@dataclass
class AutoTripSmartBehavior(Behavior):
    """complete auto trip, use zaap & change world if needed"""

    auto_trip_explorator_behavior: AutoTripExploratorBehavior
    npc_dialog_behavior: NpcDialogBehavior

    def run(self, map_ids: set[int]) -> None:
        """auto trip to one of map ids"""

        from_area_id = (
            DataReader()
            .sub_area_by_id[
                DataReader().map_pos_by_map_id[self.game_state.map.map_id].subAreaId
            ]
            .areaId
        )
        to_area_id = (
            DataReader()
            .sub_area_by_id[
                DataReader().map_pos_by_map_id[next(iter(map_ids))].subAreaId
            ]
            .areaId
        )

        if from_area_id == AreaEnum.INCARNAM and to_area_id != AreaEnum.INCARNAM:
            self.from_incarnam_go_astrub(map_ids)
        else:
            self.auto_trip_explorator_behavior.start(
                callback=self.finish, parent=self, map_ids=map_ids
            )

    def from_incarnam_go_astrub(self, dst_map_ids: set[int]):
        self.logger.info("Get out of incarnam")
        self.auto_trip_explorator_behavior.start(
            callback=partial(
                self.on_auto_trip_to_npc_portal_incarnam_finished,
                dst_map_ids=dst_map_ids,
            ),
            parent=self,
            map_ids={NPC_PORTAL_INCARNAM.npc_map_id},
        )

    def on_auto_trip_to_npc_portal_incarnam_finished(
        self, error_code: str | None, dst_map_ids: set[int]
    ):
        if error_code is not None:
            return self.finish(error_code)

        self.npc_dialog_behavior.start(
            callback=partial(
                self.on_npc_dialog_behavior_finished, dst_map_ids=dst_map_ids
            ),
            parent=self,
            npc_dialog_info=NPC_PORTAL_INCARNAM,
        )

    def on_npc_dialog_behavior_finished(
        self, error_code: str | None, dst_map_ids: set[int]
    ):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=partial(
                self.on_auto_trip_zaap_portal_incarnam_finished, dst_map_ids=dst_map_ids
            ),
            originator=self,
            once=True,
        )

    def on_auto_trip_zaap_portal_incarnam_finished(
        self, msg: MapComplementaryInformationEvent, dst_map_ids: set[int]
    ):
        self.auto_trip_explorator_behavior.start(
            callback=self.finish, parent=self, map_ids=dst_map_ids
        )
