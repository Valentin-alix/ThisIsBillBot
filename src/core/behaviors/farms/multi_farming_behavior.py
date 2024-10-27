import random
from dataclasses import dataclass, field
from functools import partial

from d3_mapping.resources.protos.game.context_pb2 import ContextCreationEvent

from src.core.behaviors.chat.chat_behavior import ChatBehavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.interactives.collect_behavior import CollectError
from src.core.behaviors.quests.dungeon_behavior import (
    DungeonBehavior,
)
from src.core.config.multi_farming import (
    ATTACKER_TRIGGER_MAP_COUNT,
    GO_DUNGEON_MAP_COUNT,
    RANDOM_CHAT_TRIGGER_MAP_COUNT,
)
from src.core.config.timings import BASE_RANGE
from src.core.logic.craft.craft import (
    get_recipes_for_job_lvl_up,
    is_not_valid_recipe_for_lvl_up_job,
)
from src.core.logic.dungeons.dungeons import get_valid_dungeon_infos
from src.exceptions import UnhandledErrorCodeException


@dataclass
class MultiFarmingBehavior(HarvesterBehavior):
    """behavior that collect on map & fight monsters & random chat & dungeons (useful to counter antibot)"""

    attacker_behavior: AttackerBehavior
    dungeon_behavior: DungeonBehavior
    chat_behavior: ChatBehavior
    craft_behavior: CraftBehavior

    _map_numero: int = field(init=False, default=0)
    _next_chat_map_numero: int = field(init=False, default=-1)
    _next_attack_map_numero: int = field(init=False, default=-1)
    _next_dungeon_map_numero: int = field(init=False, default=-1)

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

        self._map_numero += 1

        if self._next_attack_map_numero < self._map_numero:
            self._next_attack_map_numero = self._map_numero + random.randint(
                int(ATTACKER_TRIGGER_MAP_COUNT / 1.5),
                int(ATTACKER_TRIGGER_MAP_COUNT * 1.5),
            )
        if self._next_chat_map_numero < self._map_numero:
            self._next_chat_map_numero = self._map_numero + random.randint(
                int(RANDOM_CHAT_TRIGGER_MAP_COUNT / 1.5),
                int(RANDOM_CHAT_TRIGGER_MAP_COUNT * 1.5),
            )
        if self._next_dungeon_map_numero < self._map_numero:
            self._next_dungeon_map_numero = self._map_numero + random.randint(
                int(GO_DUNGEON_MAP_COUNT / 1.5),
                int(GO_DUNGEON_MAP_COUNT * 1.5),
            )

        if self._map_numero == self._next_dungeon_map_numero:
            valid_dungeons_infos = get_valid_dungeon_infos(
                self.game_state.player.level,
                self.game_state.player.is_sub,
                self.game_state.inventory.objects_by_uid,
            )
            self.logger.info(f"Valid dungeons infos : {valid_dungeons_infos}")
            if len(valid_dungeons_infos) == 0:
                return on_random_action_done()
            self.run_timer(
                BASE_RANGE,
                lambda: self.dungeon_behavior.start(
                    dungeon_info=random.choice(valid_dungeons_infos),
                    callback=lambda _: on_random_action_done(),
                    parent=self,
                ),
            )
        elif self._map_numero == self._next_chat_map_numero:
            self.run_timer(
                BASE_RANGE,
                lambda: self.chat_behavior.start(
                    callback=lambda _: on_random_action_done(), parent=self
                ),
            )
        elif self._map_numero == self._next_attack_map_numero:
            self.fight_on_map()
        else:
            on_random_action_done()

    def fight_on_map(self):
        self.attacker_behavior.start(
            count_fight_limit=1,
            behavior_context_to_clears=[self],
            parent=self,
            callback=self.on_attacker_behavior_finished,
        )

    def on_attacker_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.collect_on_map()

    def collect_on_map(self):
        self.event_manager.on(
            ContextCreationEvent, self.on_context_creation_event, originator=self
        )
        self.collect_behavior.start(
            callback=self.on_collect_behavior_finished, parent=self
        )

    def on_collect_behavior_finished(self, error_code: str | None):
        if error_code == CollectError.FULL_PODS:
            return self.on_full_pods()
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.run_next_step()

    def on_sale_hotel_price_updated_and_unloaded(self):
        recipes = get_recipes_for_job_lvl_up(
            self.game_state.player.is_sub, self.game_state.player.jobs_lvl_by_id
        )
        self.craft_behavior.start(
            recipes=recipes,
            stop_craft_recipe_condition=partial(
                is_not_valid_recipe_for_lvl_up_job,
                is_sub=self.game_state.player.is_sub,
                jobs_lvl_by_id=self.game_state.player.jobs_lvl_by_id,
            ),
            callback=lambda _: self.on_new_map(),
            parent=self,
        )
