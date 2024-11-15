import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Callable

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.farms.multi_farming_behavior import MultiFarmingBehavior
from src.core.config.auto import (
    AREAS_SUB_WITH_WEIGHT,
    AREAS_UNSUB_WITH_WEIGHT,
    DO_FIGHTER,
    KAMAS_LIMIT_FOR_HARVEST,
    LVL_LIMIT_FOR_HARVEST,
    AreaInfoWithWeight,
)
from src.core.config.timings import get_time_beween_areas
from src.core.logic.farms.weights.weight_areas import (
    get_weight_area,
    get_weight_sub_area,
)

CURRENT_AREAS_PLAYING_INFOS_BY_CHARACTER_ID: dict[int, AreaInfoWithWeight] = {}
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
    _areas_sub_with_weight: list[AreaInfoWithWeight] = field(
        init=False, default_factory=AREAS_SUB_WITH_WEIGHT.copy
    )
    _areas_unsub_with_weight: list[AreaInfoWithWeight] = field(
        init=False, default_factory=AREAS_UNSUB_WITH_WEIGHT.copy
    )
    _get_time_beween_areas_fn: Callable[[], timedelta] = field(
        init=False, default=get_time_beween_areas
    )
    _area_id: int | None = field(init=False, default=None)
    _sub_area_id: int | None = field(init=False, default=None)
    _previous_area_info_played: list[AreaInfoWithWeight] = field(
        init=False, default_factory=list
    )

    def run(
        self,
        area_id: int | None = None,
        sub_area_id: int | None = None,
        lvl_limit_for_harvest: int = LVL_LIMIT_FOR_HARVEST,
        kamas_limit_for_harvest: int = KAMAS_LIMIT_FOR_HARVEST,
        areas_sub_with_weight: list[AreaInfoWithWeight] | None = None,
        areas_unsub_with_weight: list[AreaInfoWithWeight] | None = None,
        get_time_beween_areas_fn: Callable[[], timedelta] = get_time_beween_areas,
    ) -> None:
        self._area_id = area_id
        self._sub_area_id = sub_area_id
        if areas_sub_with_weight is None:
            areas_sub_with_weight = AREAS_SUB_WITH_WEIGHT
        if areas_unsub_with_weight is None:
            areas_unsub_with_weight = AREAS_UNSUB_WITH_WEIGHT

        self._get_time_beween_areas_fn = get_time_beween_areas_fn
        self._lvl_limit_for_harvest = lvl_limit_for_harvest
        self._kamas_limit_for_harvest = kamas_limit_for_harvest
        self._areas_sub_with_weight = areas_sub_with_weight

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
            area_info = self.get_random_area_info()
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

        area_info = self.get_random_area_info()

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

    def get_random_area_info(self):
        if self._area_id is not None:
            return AreaInfoWithWeight(
                area_id=self._area_id, sub_area_id=self._sub_area_id
            )

        if self.game_state.player.is_sub:
            areas_with_weight = self._areas_sub_with_weight
        else:
            areas_with_weight = self._areas_unsub_with_weight

        weight_by_areas_info: dict[AreaInfoWithWeight, float] = {}

        for area_info in areas_with_weight:
            list(CURRENT_AREAS_PLAYING_INFOS_BY_CHARACTER_ID.values()).count(area_info)
            if area_info.sub_area_id:
                weight = get_weight_sub_area(
                    self.game_state.player.jobs_lvl_by_id,
                    self.game_state.inventory.bank_object_by_gid,
                    area_info.sub_area_id,
                    self.game_state.player.is_sub,
                )
            else:
                weight = get_weight_area(
                    self.game_state.player.jobs_lvl_by_id,
                    area_info.area_id,
                    self.game_state.player.is_sub,
                    self.game_state.inventory.bank_object_by_gid,
                )
            count_area_already_playing = list(
                CURRENT_AREAS_PLAYING_INFOS_BY_CHARACTER_ID.values()
            ).count(area_info)
            weight_by_areas_info[area_info] = weight / (
                1
                + count_area_already_playing * 3
                + self._previous_area_info_played.count(area_info)
            )

        def is_valid_area(area_info: AreaInfoWithWeight):
            return (
                self.game_state.player.level >= area_info.min_lvl
                and (
                    area_info.waypoint_id_needed is None
                    or area_info.waypoint_id_needed
                    in self.game_state.player.waypoint_map_ids
                )
                and weight_by_areas_info[area_info] > 0
            )

        areas_infos = [
            area_info for area_info in areas_with_weight if is_valid_area(area_info)
        ]

        areas_weights = [
            (weight_by_areas_info[area_info])
            for area_info in areas_with_weight
            if is_valid_area(area_info)
        ]

        self.logger.info(f"Area infos : {repr(areas_infos)} | Weight : {areas_weights}")

        return random.choices(areas_infos, weights=areas_weights, k=1)[0]
