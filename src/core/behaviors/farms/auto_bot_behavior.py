from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

from dofus_unity_reader.game_constants.area import AreaInfo

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.base_farm_behavior import BaseFarmingErrorCode
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.farms.multi_farming_behavior import MultiFarmingBehavior
from src.core.config import (
    DO_FIGHTER,
    KAMAS_LIMIT_FOR_HARVEST,
    LVL_LIMIT_FOR_HARVEST,
    get_time_beween_areas,
)
from src.core.engine.contexts import HarvesterAreaContext
from src.core.engine.weights.harvester.weight_areas import (
    get_random_best_area_info_for_harvester,
)
from src.core.states.area_state import (
    CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER,
)

AREA_CHOICE_LOCK = Lock()


@dataclass
class AutoBotBehavior(Behavior):
    """
    Behavior to fight until certain lvl & kamas then play MultiFarmingBehavior,
    This is a good behavior to automatically chose action based on context
    """

    fighter_behavior: FighterBehavior
    harvester_behavior: HarvesterBehavior
    multi_farming_behavior: MultiFarmingBehavior

    _area_id: int | None = field(init=False, default=None)
    _sub_area_id: int | None = field(init=False, default=None)
    _previous_area_info_played: list[AreaInfo] = field(
        init=False, default_factory=list[AreaInfo]
    )

    def get_harvester_area_context(self) -> HarvesterAreaContext:
        return HarvesterAreaContext(
            player_level=self.game_state.player.level,
            player_waypoint_map_ids=frozenset(self.game_state.player.waypoint_map_ids),
            player_is_sub=self.game_state.player.is_sub,
            player_server_id=self.game_state.player.server_id,
            player_jobs_lvl_by_id=self.game_state.player.jobs_lvl_by_id,
            bank_storage_by_gid=self.game_state.inventory.get_bank_objects_by_gid(),
            current_area_infos_by_server_and_character=(
                CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER
            ),
        )

    def run(
        self,
        area_id: int | None = None,
        sub_area_id: int | None = None,
    ) -> None:
        self._area_id = area_id
        self._sub_area_id = sub_area_id
        self.play()

    def play(self) -> None:
        if (
            self.game_state.player.level < LVL_LIMIT_FOR_HARVEST
            or self.game_state.inventory.kamas < KAMAS_LIMIT_FOR_HARVEST
        ) and DO_FIGHTER:
            self.play_fighter()
        else:
            self.play_multi_farming()

    def play_multi_farming(self) -> None:
        datetime_start_played = datetime.now()

        def stop_multi_farming_condition():
            return datetime_start_played + get_time_beween_areas() < datetime.now()

        with AREA_CHOICE_LOCK:
            area_info = get_random_best_area_info_for_harvester(
                self._area_id,
                self._sub_area_id,
                self.get_harvester_area_context(),
                self._previous_area_info_played,
                self.logger,
            )
            key = (
                self.game_state.player.server_id,
                self.game_state.player.character_id,
            )
            CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER[key] = area_info
            self._previous_area_info_played.append(area_info)

        self.multi_farming_behavior.start(
            area_id=area_info.area_id,
            sub_area_id=area_info.sub_area_id,
            is_stopped_at_new_map_condition=stop_multi_farming_condition,
            callback=self.on_multi_farming_behavior_finished,
            parent=self,
        )

    def on_multi_farming_behavior_finished(self, error_code: str | None) -> None:
        if error_code is BaseFarmingErrorCode.STOP_CONDITION_TRIGGERED:
            return self.play_multi_farming()
        self.finish(error_code)

    def play_fighter(self) -> None:
        datetime_start_played = datetime.now()

        def stop_condition_fighter() -> bool:
            self.logger.info(
                f"Checking condition with current lvl : {self.game_state.player.level} and kamas {self.game_state.inventory.kamas}"
            )
            return (
                self.game_state.player.level >= LVL_LIMIT_FOR_HARVEST
                and self.game_state.inventory.kamas >= KAMAS_LIMIT_FOR_HARVEST
            ) or datetime_start_played + get_time_beween_areas() < datetime.now()

        area_info = get_random_best_area_info_for_harvester(
            self._area_id,
            self._sub_area_id,
            self.get_harvester_area_context(),
            self._previous_area_info_played,
            self.logger,
        )

        self._previous_area_info_played.append(area_info)

        self.fighter_behavior.start(
            area_id=area_info.area_id,
            sub_area_id=area_info.sub_area_id,
            is_stopped_at_new_map_condition=stop_condition_fighter,
            callback=self.on_fighter_behavior_finished,
            parent=self,
        )

    def on_fighter_behavior_finished(self, error_code: str | None) -> None:
        if error_code is BaseFarmingErrorCode.STOP_CONDITION_TRIGGERED:
            return self.play()
        self.finish(error_code)
