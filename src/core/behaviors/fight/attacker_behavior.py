import random
from dataclasses import field
from functools import partial
from typing import Callable, Iterable

from d3_mapping.resources.protos.game.common_pb2 import ActorPositionInformation
from d3_mapping.resources.protos.game.context_pb2 import ContextCreationEvent
from d3_mapping.resources.protos.game.roleplay_pb2 import AttackMonsterRequest
from enums.monster_gid_enum import MonsterGidEnum
from scapy.all import dataclass

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.controller.human_timings import HumanTimingsController
from src.core.logic.map.path_finding.movement_path import MovementPath
from src.core.logic.map.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException


@dataclass
class MonsterGroupInfo:
    actor_id: int
    move_path: MovementPath
    level: int


@dataclass
class AttackerBehavior(Behavior):
    path_finding: Pathfinding
    map_move_behavior: MapMoveBehavior
    fight_behavior: FightBehavior

    _count_fight_limit: int | None = field(init=False, default=None)
    _count_fighted_on_map: int = field(init=False, default=0)
    _behavior_context_to_clears: Iterable[Behavior] | None = field(
        init=False, default=None
    )
    _wait_for_group: bool = field(init=False, default=False)
    _get_lvl_limit: Callable[[int], float] = lambda level: level * 1.5 + 5

    def run(
        self,
        count_fight_limit: int | None = 10,
        wait_for_group: bool = False,
        get_lvl_limit: Callable[[int], float] = lambda level: level * 1.5 + 5,
        behavior_context_to_clears: Iterable[Behavior] | None = None,
    ) -> None:
        self._get_lvl_limit = get_lvl_limit
        self._wait_for_group = wait_for_group
        self._behavior_context_to_clears = behavior_context_to_clears
        self._count_fighted_on_map = 0
        self._count_fight_limit = count_fight_limit
        self.attack_enemy()

    def attack_enemy(self):
        monster_group_info = self.get_next_enemy()
        if monster_group_info is None:
            if self._wait_for_group:
                return self.run_timer(0.5, self.attack_enemy)
            return self.finish()

        self.run_timer(
            HumanTimingsController().get_timing_attack_on_new_map(),
            lambda: self.map_move_behavior.start(
                callback=partial(
                    self.on_moved_to_monster, group_actor_id=monster_group_info.actor_id
                ),
                parent=self,
                move_path=monster_group_info.move_path,
            ),
        )

    def on_moved_to_monster(self, error_code: str | None, group_actor_id: int) -> None:
        if error_code is not None:
            if error_code is MapMoveError.INVALID_STARTING_POINT:
                return self.attack_enemy()
            raise UnhandledErrorCodeException(error_code)

        related_actor = self.game_state.entity.actor_by_id.get(group_actor_id)
        if (
            related_actor is None
            or related_actor.disposition.cell_id
            != self.game_state.player.map_point.cell_id
        ):
            self.logger.info(
                f"Monster group moved out of mp {self.game_state.player.map_point.cell_id} or is not there anymore, "
                f"skipping."
            )
            return self.attack_enemy()

        with self.event_manager.lock:
            self.event_manager.clear_listener_by_origin_and_type(
                ContextCreationEvent, self
            )
            if self._behavior_context_to_clears is not None:
                for behavior in self._behavior_context_to_clears:
                    self.event_manager.clear_listener_by_origin_and_type(
                        ContextCreationEvent, behavior
                    )
            self.event_manager.on(
                msg_type=ContextCreationEvent,
                callback=self.on_context_creation_event,
                originator=self,
                once=True,
                timeout=10,
                on_timeout=self.attack_enemy,
            )
        request = AttackMonsterRequest(monster_group_id=group_actor_id)
        self.event_manager.send(request)

    def on_context_creation_event(self, msg: ContextCreationEvent):
        if msg.context == ContextCreationEvent.GameContext.FIGHT:
            self.fight_behavior.start(
                callback=self.on_fight_behavior_finish,
                parent=self,
            )

    def on_fight_behavior_finish(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self._count_fighted_on_map += 1
        if (
            self._count_fight_limit is not None
            and self._count_fighted_on_map >= self._count_fight_limit
        ):
            return self.finish()
        self.attack_enemy()

    def get_next_enemy(self) -> MonsterGroupInfo | None:
        monster_group_infos: list[MonsterGroupInfo] = []
        for (
            actor_id,
            mp_group,
            monster_group,
        ) in self.game_state.entity.get_monster_groups():
            monster_group_lvl = self.get_level_monster_group(monster_group)
            if not self.is_valid_monster_group(monster_group, monster_group_lvl):
                continue
            move_path_to_group = self.path_finding.find_path(
                self.game_state.player.map_point,
                {mp_group},
            )
            if move_path_to_group.end != mp_group:
                continue
            monster_group_infos.append(
                MonsterGroupInfo(
                    actor_id=actor_id,
                    move_path=move_path_to_group,
                    level=monster_group_lvl,
                )
            )

        if len(monster_group_infos) == 0:
            return None

        return random.choices(
            monster_group_infos,
            [
                self.get_weight_monster_group_info(monster_group_info)
                for monster_group_info in monster_group_infos
            ],
        )[0]

    def is_valid_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
        monster_group_lvl: int,
    ) -> bool:
        if monster_group.identification.main_creature.gid in [
            MonsterGidEnum.POUTCH,
            MonsterGidEnum.PRESPIC,
        ]:
            return False
        group_lvl = self._get_lvl_limit(self.game_state.player.limited_lvl)
        self.logger.info(
            f"Group lvl : {group_lvl} against monster group lvl : {monster_group_lvl}"
        )
        return monster_group_lvl <= group_lvl

    def get_level_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ):
        total_group_lvl = 0
        total_group_lvl += monster_group.identification.main_creature.level
        for underling in monster_group.identification.underlings:
            total_group_lvl += underling.level
        return total_group_lvl

    def get_weight_monster_group_info(
        self,
        monster_group_info: MonsterGroupInfo,
    ) -> float:
        duration_move = MovementPath.get_total_duration(
            monster_group_info.move_path.path,
            self.game_state.inventory.inventory_weight,
            self.game_state.inventory.weight_max,
        )
        return (1 + monster_group_info.level) / (1 + duration_move**2)
