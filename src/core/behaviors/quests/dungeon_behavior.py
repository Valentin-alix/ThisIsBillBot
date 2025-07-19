from dataclasses import dataclass
from functools import partial

from datas.protos.non_obf.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.dungeon_info import PLAYABLE_DUNGEONS, DungeonInfo
from dofus_unity_reader.data_center.i18n import I18N

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npcs.npc_dialog_behavior import NpcDialogBehavior
from src.core.config import ON_NEW_MAP_BEFORE_ACTION
from src.core.engine.dungeons.dungeon_access import (
    do_have_key_access_to_dungeon,
)


@dataclass
class DungeonBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior
    attacker_behavior: AttackerBehavior
    auto_trip_smart_behavior: AutoTripSmartBehavior

    def run(self, dungeon_info: DungeonInfo | None = None) -> None:
        if dungeon_info is None:
            dungeon_info = next(
                (
                    _dungeon_info
                    for _dungeon_info in PLAYABLE_DUNGEONS
                    if do_have_key_access_to_dungeon(
                        _dungeon_info,
                        self.game_state.inventory.objects_by_uid,
                        self.logger,
                    )
                ),
                None,
            )
            if dungeon_info is None:
                return self.finish()

        self.auto_trip_smart_behavior.start(
            map_ids={dungeon_info.entrance_npc_info.npc_map_id},
            callback=partial(
                self.on_auto_trip_smart_behavior_to_entrance_finished,
                dungeon_info=dungeon_info,
            ),
            parent=self,
        )

    def on_auto_trip_smart_behavior_to_entrance_finished(
        self, error_code: str | None, dungeon_info: DungeonInfo
    ) -> None:
        if error_code is not None:
            return self.exit_dungeon(dungeon_info)

        self.npc_dialog_behavior.start(
            npc_dialog_info=dungeon_info.entrance_npc_info,
            callback=self.on_npc_dialog_behavior_finished,
            parent=self,
        )

    def on_npc_dialog_behavior_finished(self, error_code: str | None, dungeon_info: DungeonInfo) -> None:
        self.event_manager.on(
            MapComplementaryInformationEvent,
            lambda _: self.on_new_map(dungeon_info),
            originator=self,
            once=True,
        )

    def on_new_map(self, dungeon_info: DungeonInfo) -> None:
        if self.game_state.map.map_id not in dungeon_info.dungeon.mapIds:
            return self.exit_dungeon(dungeon_info)

        def get_lvl_limit(_: int) -> float:
            return float("inf")

        self.attacker_behavior.start(
            count_fight_limit=1,
            wait_for_group=True,
            get_lvl_limit=get_lvl_limit,
            callback=partial(self.on_attacker_behavior_finished, dungeon_info=dungeon_info),
            parent=self,
        )

    def on_attacker_behavior_finished(
        self,
        error_code: str | None,
        count_fighted_on_map: int,
        dungeon_info: DungeonInfo,
    ) -> None:
        self.on_new_map(dungeon_info)

    def exit_dungeon(self, dungeon_info: DungeonInfo) -> None:
        map_name_id = DataReader().map_info_by_map_id[self.game_state.map.map_id].nameId
        title_map = I18N().name_by_id[map_name_id] if map_name_id in I18N().name_by_id else ""
        if "Sortie" in title_map:
            self.event_manager.on(
                MapComplementaryInformationEvent,
                callback=self.on_new_map_after_exit_dungeon,
                originator=self,
                once=True,
            )
            self.run_timer(
                ON_NEW_MAP_BEFORE_ACTION,
                lambda: self.npc_dialog_behavior.start(
                    npc_dialog_info=dungeon_info.exit_npc_info,
                    callback=None,
                    parent=self,
                ),
            )
        else:
            self.finish()

    def on_new_map_after_exit_dungeon(self, msg: MapComplementaryInformationEvent) -> None:
        self.finish()
