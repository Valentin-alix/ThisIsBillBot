import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from src.core.behaviors.communication.chat_behavior import ChatBehavior
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.quests.dungeon_behavior import (
    DungeonBehavior,
)
from src.core.config import (
    BASE_RANGE,
    get_time_between_attacker,
    get_time_between_dungeon,
    get_time_between_random_chat,
)
from src.core.engine.dungeons.dungeon_access import get_valid_dungeon_infos
from src.exceptions import UnhandledErrorCodeException


@dataclass
class MultiFarmingBehavior(HarvesterBehavior):
    """behavior that collect on map & fight monsters & random chat & dungeons (useful to counter antibot)"""

    attacker_behavior: AttackerBehavior
    dungeon_behavior: DungeonBehavior
    chat_behavior: ChatBehavior

    _next_time_chat: datetime = field(init=False, default_factory=datetime.now)
    _next_time_attacker: datetime = field(init=False, default_factory=datetime.now)
    _next_time_dungeon: datetime = field(init=False, default_factory=datetime.now)

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        stop_condition_with_callback: tuple[Callable[[], bool], Callable[[], None]]
        | None = None,
    ):
        self._next_time_chat = datetime.now() + get_time_between_random_chat()
        self._next_time_attacker = datetime.now() + get_time_between_attacker()
        self._next_time_dungeon = datetime.now() + get_time_between_dungeon()
        return super().run(area_id, sub_area_id, stop_condition_with_callback)

    def on_new_map(self):
        if self._stop_condition_with_callback is not None:
            stop_condition, callback = self._stop_condition_with_callback
            if stop_condition():
                self.logger.info("Stop condition triggered, let's call callback")
                self.finish()
                return callback()

        def on_random_action_done():
            if self.game_state.map.map_id in self.random_farm_behavior.map_ids:
                self.collect_on_map()
            else:
                self.run_next_step()

        def on_chat_behavior_finished(error_code: str | None):
            self._next_time_chat = datetime.now() + get_time_between_random_chat()
            on_random_action_done()

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
                BASE_RANGE,
                lambda: self.dungeon_behavior.start(
                    dungeon_info=random.choice(valid_dungeons_infos),
                    callback=on_dungeon_behavior_finished,
                    parent=self,
                ),
            )

        if self._next_time_chat <= datetime.now():
            self.logger.info("Time to chat !")
            is_other_character_in_map = any(
                actor_id != self.game_state.player.character_id and actor_id > 0
                for actor_id in self.game_state.entity.actor_by_id.keys()
            )
            if is_other_character_in_map:
                self.logger.info(
                    "There is other character in current map, skip chat for now !"
                )
            else:
                return self.run_timer(
                    BASE_RANGE,
                    lambda: self.chat_behavior.start(
                        callback=on_chat_behavior_finished, parent=self
                    ),
                )

        if self._next_time_attacker <= datetime.now():
            self.logger.info("Time to attack !")
            return self.fight_on_map()

        on_random_action_done()

    def fight_on_map(self):
        self.attacker_behavior.start(
            count_fight_limit=1,
            behavior_context_to_clears=[self],
            parent=self,
            callback=self.on_attacker_behavior_finished,
        )

    def on_attacker_behavior_finished(
        self, error_code: str | None, count_fighted_on_map: int
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        if count_fighted_on_map >= 1:
            self._next_time_attacker = datetime.now() + get_time_between_attacker()
        self.collect_on_map()

    def collect_on_map(self):
        self.collect_behavior.start(
            callback=self.on_collect_behavior_finished, parent=self
        )
