from datetime import datetime
import random
from dataclasses import dataclass

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fighter.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvest.harvester_behavior import HarvesterBehavior
from src.core.config.suicide_bots import (
    FIGHTABLE_AREAS_SUB_WITH_WEIGHT,
    FIGHTABLE_AREAS_UNSUB_WITH_WEIGHT,
    FIGHTER_WEIGHT_ACTION,
    HARVESTABLE_AREAS_SUB_WITH_WEIGHT,
    HARVESTABLE_AREAS_UNSUB_WITH_WEIGHT,
    HARVESTER_WEIGHT_ACTION,
)
from src.core.config.timings import TIME_FIGHTER, TIME_HARVESTER


@dataclass
class SuicideBotBehavior(Behavior):
    fighter_behavior: FighterBehavior
    harvester_behavior: HarvesterBehavior

    def run(self) -> None:
        if (
            self.game_state.player.level < 10
            or self.game_state.inventory.kamas < 10_000
        ):
            self.play_fighter()
        else:
            random_action = random.choices(
                (self.play_harvester, self.play_fighter),
                weights=[HARVESTER_WEIGHT_ACTION, FIGHTER_WEIGHT_ACTION],
            )[0]
            random_action()

    def play_harvester(self):
        if self.fighter_behavior.is_running.is_set():
            self.fighter_behavior.finish()

        if self.game_state.player.is_sub:
            areas_infos = HARVESTABLE_AREAS_SUB_WITH_WEIGHT
        else:
            areas_infos = HARVESTABLE_AREAS_UNSUB_WITH_WEIGHT

        area_info = [
            area_info
            for area_info, _, min_level in areas_infos
            if self.game_state.player.level >= min_level
        ]
        if len(area_info) == 0:
            self.logger.warning(
                "No valid area for harvester, let's play fighter instead"
            )
            return self.play_fighter()

        area_weight = [
            weight
            for _, weight, min_level in areas_infos
            if self.game_state.player.level >= min_level
        ]

        self.harvester_behavior.start(
            **random.choices(area_info, weights=area_weight)[0],
            callback_on_time_limit=(
                self.play_fighter,
                datetime.now() + TIME_HARVESTER,
            ),
            callback=None,
            parent=self,
        )

    def play_fighter(self):
        if self.harvester_behavior.is_running.is_set():
            self.harvester_behavior.finish()

        if self.game_state.player.is_sub:
            areas_infos = FIGHTABLE_AREAS_SUB_WITH_WEIGHT
        else:
            areas_infos = FIGHTABLE_AREAS_UNSUB_WITH_WEIGHT

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

        self.fighter_behavior.start(
            **random.choices(area_info, weights=area_weight)[0],
            callback_on_time_limit=(
                self.play_harvester,
                datetime.now() + TIME_FIGHTER,
            ),
            callback=None,
            parent=self,
        )
