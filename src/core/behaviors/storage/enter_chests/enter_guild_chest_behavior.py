from dataclasses import dataclass
from enum import StrEnum, auto
from typing import cast

from d3_mapping.resources.protos.game.inventory_pb2 import StorageInventoryContentEvent
from data_center.map_reader import MapReader
from enums.element_type import ElementTypeEnum
from grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.consts import BANK_MAP_IDS
from src.core.config.timings import BASE_RANGE
from src.core.logic.map.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException


class EnterGuildChestError(StrEnum):
    CANT_ACCESS_GUILD_CHEST = auto()


@dataclass
class EnterGuildChestBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    auto_trip_world_behavior: AutoTripSmartBehavior

    def run(self):
        if not self.game_state.player.can_access_guild_chest:
            return self.finish(error_code=EnterGuildChestError.CANT_ACCESS_GUILD_CHEST)

        self.auto_trip_world_behavior.start(
            callback=self.on_bank_map,
            parent=self,
            map_ids={bank_map_id for bank_map_id in BANK_MAP_IDS},
        )

    def on_bank_map(self, error_code: str | None):
        if error_code is not None:
            return self.logger.error(error_code)

        chest_interactive = next(
            element
            for element in self.game_state.interactive.interactive_element_by_id.values()
            if element.element_type_id == ElementTypeEnum.GUILD_CHEST
        )
        ref_data = MapReader().get_ref_data_by_element_id(self.game_state.map.map_id)[
            chest_interactive.element_id
        ]

        move_path_to_chest = self.path_finding.find_path(
            self.game_state.player.map_point,
            {MapPoint.from_cell_id(cast(int, ref_data.cellId))},
        )

        self.run_timer(
            BASE_RANGE,
            lambda: self.interactive_behavior.start(
                move_path=move_path_to_chest,
                element_id=chest_interactive.element_id,
                skill_instance_uid=chest_interactive.enabled_skills[
                    0
                ].skill_instance_uid,
                callback=self.on_interactive_behavior_finished,
                parent=self,
            ),
        )

    def on_interactive_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.event_manager.on(
            StorageInventoryContentEvent,
            lambda _: self.finish(),
            originator=self,
            once=True,
        )
