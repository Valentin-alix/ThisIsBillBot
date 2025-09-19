from dataclasses import dataclass
from enum import StrEnum, auto

from datas.protos.non_obf.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
)
from dofus_unity_reader.data_center.map_reader import MapReader
from dofus_unity_reader.game_constants.element_type import ElementTypeEnum
from dofus_unity_reader.game_constants.map_id import BANK_MAP_IDS
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.recovery import RecoverableBehavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.services.human_timings import HumanTimingsService
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.states.dialog_state import OpenDialogKind


class EnterGuildChestError(StrEnum):
    CANT_ACCESS_GUILD_CHEST = auto()


@dataclass
class EnterGuildChestBehavior(RecoverableBehavior):
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    auto_trip_world_behavior: AutoTripSmartBehavior

    def run(self) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(lambda: self.start_entering_guild_chest())

    def start_entering_guild_chest(self):
        if not self.game_state.guild_chest.can_access_guild_chest:
            return self.finish(error_code=EnterGuildChestError.CANT_ACCESS_GUILD_CHEST)

        if self.game_state.dialog.is_open(OpenDialogKind.GUILD_CHEST):
            self.logger.info("Guild chest already open, reusing it")
            return self.finish()

        self.auto_trip_world_behavior.start(
            callback=self.on_bank_map,
            parent=self,
            map_ids=set(BANK_MAP_IDS),
        )

    def on_bank_map(self, error_code: str | None):
        if error_code is not None:
            return self.logger.error(error_code)

        chest_interactive = next(
            element
            for element in self.game_state.interactive.interactive_element_by_id.values()
            if element.element_type_id == ElementTypeEnum.GUILD_CHEST
        )
        ref_data = MapReader().get_ref_data_by_element_id_by_map_id(self.game_state.map.map_id)[
            chest_interactive.element_id
        ]
        if ref_data.cellId is None:
            raise ValueError("Guild chest cell id is missing")
        element_mp = MapPoint.from_cell_id(ref_data.cellId)

        self.run_timer(
            HumanTimingsService().get_timing_base_action(),
            lambda: self.interactive_behavior.start(
                element_mp=element_mp,
                element_id=chest_interactive.element_id,
                callback=self.on_interactive_behavior_finished,
                parent=self,
            ),
        )

    def on_interactive_behavior_finished(self, error_code: str | None):
        self.raise_if_error(error_code)

        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            lambda _: self.finish(),
            originator=self,
            once=True,
        )
