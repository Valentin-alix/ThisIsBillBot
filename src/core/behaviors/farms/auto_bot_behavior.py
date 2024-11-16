from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Callable

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.farms.multi_farming_behavior import MultiFarmingBehavior
from src.core.config import (
    DO_FIGHTER,
    KAMAS_LIMIT_FOR_HARVEST,
    LVL_LIMIT_FOR_HARVEST,
    get_time_beween_areas,
)
from src.core.engine.movements.area_infos import (
    AreaInfo,
)
from src.core.engine.weights.harvester.weight_areas import (
    get_random_best_area_info_for_harvester,
)
from src.core.states.area_state import CURRENT_AREAS_PLAYING_INFOS_BY_CHARACTER_ID

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

    _lvl_limit_for_harvest: int = field(init=False, default=LVL_LIMIT_FOR_HARVEST)
    _kamas_limit_for_harvest: int = field(init=False, default=KAMAS_LIMIT_FOR_HARVEST)
    _get_time_beween_areas_fn: Callable[[], timedelta] = field(
        init=False, default=get_time_beween_areas
    )
    _area_id: int | None = field(init=False, default=None)
    _sub_area_id: int | None = field(init=False, default=None)
    _previous_area_info_played: list[AreaInfo] = field(init=False, default_factory=list)

    def run(
        self,
        area_id: int | None = None,
        sub_area_id: int | None = None,
        lvl_limit_for_harvest: int = LVL_LIMIT_FOR_HARVEST,
        kamas_limit_for_harvest: int = KAMAS_LIMIT_FOR_HARVEST,
        get_time_beween_areas_fn: Callable[[], timedelta] = get_time_beween_areas,
    ) -> None:
        self._area_id = area_id
        self._sub_area_id = sub_area_id
        self._get_time_beween_areas_fn = get_time_beween_areas_fn
        self._lvl_limit_for_harvest = lvl_limit_for_harvest
        self._kamas_limit_for_harvest = kamas_limit_for_harvest

        if (
            self.game_state.player.level < self._lvl_limit_for_harvest
            or self.game_state.inventory.kamas < self._kamas_limit_for_harvest
            and DO_FIGHTER
        ):
            self.play_fighter()
        else:
            self.play_multi_farming()

    def play_multi_farming(self):
        datetime_start_played = datetime.now()

        def stop_multi_farming_condition():
            return (
                datetime_start_played + self._get_time_beween_areas_fn()
                < datetime.now()
            )

        with AREA_CHOICE_LOCK:
            area_info = get_random_best_area_info_for_harvester(
                self._area_id,
                self._sub_area_id,
                self.game_state,
                self._previous_area_info_played,
                self.logger,
            )
            CURRENT_AREAS_PLAYING_INFOS_BY_CHARACTER_ID[
                self.game_state.player.character_id
            ] = area_info
            self._previous_area_info_played.append(area_info)

        self.multi_farming_behavior.start(
            area_id=area_info.area_id,
            sub_area_id=area_info.sub_area_id,
            stop_condition_with_callback=(
                stop_multi_farming_condition,
                lambda: self.play_multi_farming(),
            ),
            callback=None,
            parent=self,
        )

    def play_fighter(self):
        datetime_start_played = datetime.now()

        def stop_condition_fighter() -> bool:
            self.logger.info(
                f"Checking condition with current lvl : {self.game_state.player.level} and kamas {self.game_state.inventory.kamas}"
            )
            return (
                (
                    self.game_state.player.level >= self._lvl_limit_for_harvest
                    and self.game_state.inventory.kamas >= self._kamas_limit_for_harvest
                )
                or datetime_start_played + self._get_time_beween_areas_fn()
                < datetime.now()
            )

        area_info = get_random_best_area_info_for_harvester(
            self._area_id,
            self._sub_area_id,
            self.game_state,
            self._previous_area_info_played,
            self.logger,
        )

        self._previous_area_info_played.append(area_info)

        self.fighter_behavior.start(
            area_id=area_info.area_id,
            sub_area_id=area_info.sub_area_id,
            stop_condition_with_callback=(
                stop_condition_fighter,
                lambda: self.play_multi_farming(),
            ),
            callback=None,
            parent=self,
        )
