from dataclasses import dataclass
from functools import partial

from d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_explorator_behavior import (
    AutoTripExploratorBehavior,
)
from src.core.behaviors.npc_dialog_behavior import NpcInfo, NpcDialogBehavior
from data_center.data_reader import DataReader
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.area_enum import AreaEnum

NPC_PORTAL_INCARNAM = NpcInfo(
    npc_map_id=153880835,
    npc_action_id=3,
    npc_id=-20001,
    reply_ids=[36982, 36980],
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
            raise UnhandledErrorCodeException(error_code)

        self.npc_dialog_behavior.start(
            callback=partial(
                self.on_npc_dialog_portal_incarnam_finished, dst_map_ids=dst_map_ids
            ),
            parent=self,
            npc_info=NPC_PORTAL_INCARNAM,
        )

    def on_npc_dialog_portal_incarnam_finished(
        self, error_code: str | None, dst_map_ids: set[int]
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

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
