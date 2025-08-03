import random
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from context_pb2 import ContextCreationEvent
from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
)

from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.idle_behavior import IdleBehavior
from src.core.behaviors.quests.dungeon_behavior import (
    DungeonBehavior,
)
from src.core.config import (
    AFK_PROBABILITY_PER_MAP,
    get_time_between_attacker,
    get_time_between_dungeon,
)
from src.core.engine.dungeons.dungeon_access import get_valid_dungeon_infos
from src.services.human_timings import HumanTimingsService


@dataclass
class MultiFarmingBehavior(HarvesterBehavior):
    """behavior that collect on map & fight monsters & dungeons (useful to counter antibot)"""

    attacker_behavior: AttackerBehavior
    dungeon_behavior: DungeonBehavior
    idle_behavior: IdleBehavior

    _next_time_attacker: datetime = field(init=False, default_factory=datetime.now)
    _next_time_dungeon: datetime = field(init=False, default_factory=datetime.now)
    _next_long_break_at: datetime = field(init=False, default_factory=datetime.now)

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        is_stopped_at_new_map_condition: Callable[[], bool] | None = None,
    ) -> None:
        self._next_time_attacker = datetime.now() + get_time_between_attacker()
        self._next_time_dungeon = datetime.now() + get_time_between_dungeon()
        self._schedule_next_long_break()
        return super().run(area_id, sub_area_id, is_stopped_at_new_map_condition)

    def on_new_map(self):
        if self.check_stop_condition():
            return

        if datetime.now() >= self._next_long_break_at:
            break_duration = HumanTimingsService().get_timing_farm_long_break_duration()
            self.logger.info(f"Taking a long break: {break_duration / 60:.1f}min")
            return self.idle_behavior.start(
                duration=break_duration,
                callback=self.on_long_break_finished,
                parent=self,
            )

        if random.random() < AFK_PROBABILITY_PER_MAP:
            afk_duration = HumanTimingsService().get_timing_farm_afk_break()
            self.logger.info(f"Taking an AFK break: {afk_duration:.0f}s")
            return self.idle_behavior.start(
                duration=afk_duration,
                callback=self.on_idle_behavior_finished,
                parent=self,
            )

        self._continue_on_new_map()

    def on_long_break_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self._schedule_next_long_break()
        self._continue_on_new_map()

    def _schedule_next_long_break(self) -> None:
        interval_seconds = HumanTimingsService().get_timing_farm_long_break_interval()
        self._next_long_break_at = datetime.now() + timedelta(seconds=interval_seconds)

    def on_idle_behavior_finished(self, error_code: str | None):
        self._continue_on_new_map()

    def _continue_on_new_map(self):
        if self.check_stop_condition():
            return

        def on_random_action_done():
            HarvesterBehavior.on_new_map(self)

        def on_dungeon_behavior_finished(error_code: str | None):
            self._next_time_dungeon = datetime.now() + get_time_between_dungeon()
            on_random_action_done()

        if self._next_time_dungeon <= datetime.now():
            self.logger.info("Time to dungeon !")
            valid_dungeons_infos = get_valid_dungeon_infos(
                self.game_state.player.level,
                self.game_state.player.is_sub,
                self.game_state.inventory.objects_by_uid,
                self.logger,
            )
            self.logger.info(f"Valid dungeons infos : {valid_dungeons_infos}")
            if len(valid_dungeons_infos) == 0:
                return on_dungeon_behavior_finished(None)
            return self.run_timer(
                HumanTimingsService().get_timing_base_action(),
                lambda: self.dungeon_behavior.start(
                    dungeon_info=random.choice(valid_dungeons_infos),
                    callback=on_dungeon_behavior_finished,
                    parent=self,
                ),
            )

        if self._next_time_attacker <= datetime.now():
            self.logger.info("Time to attack !")
            force_attack = False
            if datetime.now() - self._next_time_attacker > (get_time_between_attacker() * 1.5):
                self.logger.info("We really need to attack to counter antibot, so force attack")
                force_attack = True
            return self.fight_on_map(force_attack)

        on_random_action_done()

    def fight_on_map(self, force_attack: bool):
        with self.event_manager.lock:
            self.unregister_listener(FightMapInformationEvent)
            self.attacker_behavior.start(
                count_fight_limit=1,
                force_attack=force_attack,
                parent=self,
                callback=self.on_attacker_behavior_finished,
            )

    def on_attacker_behavior_finished(self, error_code: str | None, count_fighted_on_map: int):
        self.raise_if_error(error_code)
        self.init_listeners()
        HarvesterBehavior.on_new_map(self)

    def on_context_creation_event(self, msg: ContextCreationEvent):
        self._next_time_attacker = datetime.now() + get_time_between_attacker()
        return super().on_context_creation_event(msg)
