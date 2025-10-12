from dataclasses import dataclass, field
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npcs.npc_dialog_behavior import NpcDialogBehavior
from src.core.engine.dungeons.dungeon_access import (
    do_have_key_access_to_dungeon,
)
from src.core.engine.dungeons.dungeon_info import DungeonInfo, PLAYABLE_DUNGEONS


@dataclass
class DungeonBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior
    attacker_behavior: AttackerBehavior
    auto_trip_smart_behavior: AutoTripSmartBehavior

    _activity_performed: bool = field(init=False, default=False)

    @property
    def activity_performed(self) -> bool:
        return self._activity_performed

    def run(self, dungeon_info: DungeonInfo | None = None) -> None:
        self._activity_performed = False
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

        if self.game_state.map.map_id in dungeon_info.dungeon.mapIds:
            return self.on_new_map(dungeon_info)
        if self.game_state.map.map_id == dungeon_info.exit_dialog_map_id:
            return self.exit_dungeon(dungeon_info)

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
            turn_variants=[dungeon_info.entrance_turns],
            callback=partial(self.on_npc_dialog_behavior_finished, dungeon_info=dungeon_info),
            parent=self,
        )

    def on_npc_dialog_behavior_finished(self, error_code: str | None, dungeon_info: DungeonInfo) -> None:
        if error_code is not None:
            return self.finish(error_code)
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
        if count_fighted_on_map > 0:
            self._activity_performed = True
        self.on_new_map(dungeon_info)

    def exit_dungeon(self, dungeon_info: DungeonInfo) -> None:
        if self.game_state.map.map_id != dungeon_info.exit_dialog_map_id:
            return self.finish()

        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=self.on_new_map_after_exit_dungeon,
            originator=self,
            once=True,
        )
        self.npc_dialog_behavior.start(
            npc_dialog_info=dungeon_info.exit_npc_info,
            turn_variants=[dungeon_info.exit_turns],
            callback=self.on_exit_npc_dialog_behavior_finished,
            parent=self,
        )

    def on_exit_npc_dialog_behavior_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            self.finish(error_code)

    def on_new_map_after_exit_dungeon(self, msg: MapComplementaryInformationEvent) -> None:
        self.finish()
