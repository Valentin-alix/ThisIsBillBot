import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.farms.multi_farming_behavior import MultiFarmingBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestErrorCode,
)
from src.core.config.auto import (
    AREAS_SUB_WITH_WEIGHT,
    AREAS_UNSUB_WITH_WEIGHT,
    KAMAS_LIMIT_FOR_HARVEST,
    LVL_LIMIT_FOR_HARVEST,
    AreaInfoWithWeight,
)
from src.core.config.timings import get_time_beween_areas
from src.exceptions import UnhandledErrorCodeException


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

    def run(
        self,
        lvl_limit_for_harvest: int = LVL_LIMIT_FOR_HARVEST,
        kamas_limit_for_harvest: int = KAMAS_LIMIT_FOR_HARVEST,
        areas_sub_with_weight: list[AreaInfoWithWeight] | None = None,
        areas_unsub_with_weight: list[AreaInfoWithWeight] | None = None,
        get_time_beween_areas_fn: Callable[[], timedelta] = get_time_beween_areas,
    ) -> None:
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

        area_info = self.get_random_area_info()
        self.multi_farming_behavior.start(
            **area_info,
            stop_condition_with_callback=(
                stop_multi_farming_condition,
                self.play_multi_farming,
            ),
            callback=None,
            parent=self,
        )

    def on_multi_farming_behavior_finished(self, error_code: str | None):
        if error_code in [
            EnterBankChestErrorCode.NOT_ENOUGH_KAMAS,
            EnterBankChestErrorCode.NOT_ENOUGH_LVL,
        ]:
            return self.play_fighter()
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)

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

        def on_stopped_by_condition_fighter():
            if (
                self.game_state.player.level >= self._lvl_limit_for_harvest
                and self.game_state.inventory.kamas >= self._kamas_limit_for_harvest
            ):
                self.play_fighter()
            else:
                self.play_multi_farming()

        area_info = self.get_random_area_info()
        self.fighter_behavior.start(
            **area_info,
            stop_condition_with_callback=(
                stop_condition_fighter,
                on_stopped_by_condition_fighter,
            ),
            callback=None,
            parent=self,
        )

    def get_random_area_info(self):
        if self.game_state.player.is_sub:
            areas_infos = self._areas_sub_with_weight
        else:
            areas_infos = self._areas_unsub_with_weight

        area_info = [
            area_info
            for area_info, _, min_level in areas_infos
            if self.game_state.player.level >= min_level
        ]
        area_weight = [
            weight
            for _, weight, min_level in areas_infos
            if self.game_state.player.level >= min_level
        ]

        return random.choices(area_info, weights=area_weight)[0]
