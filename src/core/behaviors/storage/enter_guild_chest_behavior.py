from dataclasses import dataclass
from enum import StrEnum, auto
from typing import cast

from d3_mapping.resources.protos.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.consts import BANK_MAP_IDS
from data_center.map_reader import MapReader
from grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.element_type import ElementTypeEnum


class EnterGuildChestError(StrEnum):
    DOES_NOT_RESPECT_CONDITION = auto()


@dataclass
class EnterGuildChestBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    auto_trip_world_behavior: AutoTripSmartBehavior

    def run(self):
        if not self.game_state.player.is_sub:
            return self.finish(
                error_code=EnterGuildChestError.DOES_NOT_RESPECT_CONDITION
            )

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

        self.interactive_behavior.start(
            move_path=move_path_to_chest,
            element_id=chest_interactive.element_id,
            skill_instance_uid=chest_interactive.enabled_skills[0].skill_instance_uid,
            callback=self.on_interactive_behavior_finished,
            parent=self,
        )

    def on_interactive_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            self.on_guild_chest_current_listeners_add_event,
            originator=self,
            once=True,
        )

    def on_guild_chest_current_listeners_add_event(
        self, msg: GuildChestCurrentListenersAddEvent
    ):
        self.finish()
