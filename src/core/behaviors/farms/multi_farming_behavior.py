import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
)

from src.core.behaviors.communication.chat_behavior import ChatBehavior
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.idle_behavior import IdleBehavior
from src.core.behaviors.quests.dungeon_behavior import (
    DungeonBehavior,
)
from src.core.config import (
    AFK_DURATION_RANGE,
    AFK_PROBABILITY_PER_MAP,
    BASE_RANGE,
    get_time_between_attacker,
    get_time_between_dungeon,
    get_time_between_random_chat,
)
from src.core.engine.dungeons.dungeon_access import get_valid_dungeon_infos


@dataclass
class MultiFarmingBehavior(HarvesterBehavior):
    """behavior that collect on map & fight monsters & random chat & dungeons (useful to counter antibot)"""

    attacker_behavior: AttackerBehavior
    dungeon_behavior: DungeonBehavior
    chat_behavior: ChatBehavior
    idle_behavior: IdleBehavior

    _next_time_chat: datetime = field(init=False, default_factory=datetime.now)
    _next_time_attacker: datetime = field(init=False, default_factory=datetime.now)
    _next_time_dungeon: datetime = field(init=False, default_factory=datetime.now)

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        is_stopped_at_new_map_condition: Callable[[], bool] | None = None,
    ) -> None:
        self._next_time_chat = datetime.now() + get_time_between_random_chat()
        self._next_time_attacker = datetime.now() + get_time_between_attacker()
        self._next_time_dungeon = datetime.now() + get_time_between_dungeon()
        return super().run(area_id, sub_area_id, is_stopped_at_new_map_condition)

    def on_new_map(self):
        if self.check_stop_condition():
            return

        if random.random() < AFK_PROBABILITY_PER_MAP:
            afk_duration = random.uniform(*AFK_DURATION_RANGE)
            self.logger.info(f"Taking an AFK break: {afk_duration:.0f}s")
            return self.idle_behavior.start(
                duration=afk_duration,
                callback=self._continue_on_new_map,
                parent=self,
            )

        self._continue_on_new_map()

    def _continue_on_new_map(self):
        if self.check_stop_condition():
            return

        def on_random_action_done():
            HarvesterBehavior.on_new_map(self)

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
            force_attack = False
            if datetime.now() - self._next_time_attacker > (
                get_time_between_attacker() * 1.5
            ):
                self.logger.info(
                    "We really need to attack to counter antibot, so force attack"
                )
                force_attack = True
            return self.fight_on_map(force_attack)

        on_random_action_done()

    def fight_on_map(self, force_attack: bool):
        self.unregister_listener(FightMapInformationEvent)
        self.attacker_behavior.start(
            count_fight_limit=1,
            force_attack=force_attack,
            parent=self,
            callback=self.on_attacker_behavior_finished,
        )

    def on_attacker_behavior_finished(
        self, error_code: str | None, _count_fighted_on_map: int
    ):
        self.raise_if_error(error_code)
        self.init_listeners()
        HarvesterBehavior.on_new_map(self)

    def on_fight_aggro(self):
        self._next_time_attacker = datetime.now() + get_time_between_attacker()
        return super().on_fight_aggro()
