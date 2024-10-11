import random
from dataclasses import dataclass
from functools import partial

from protos.game.common_pb2 import ActorPositionInformation
from protos.game.context_pb2 import ContextCreationEvent
from protos.game.roleplay_pb2 import AttackMonsterRequest
from src.const import ON_NEW_MAP_BEFORE_ACTION
from src.core.behaviors.bank.unload_behavior import UnloadBehavior
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.data_center.data_reader import DataReader
from src.core.logic.flags.map_position_flags import allow_monster_agression
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException


@dataclass
class MonsterGroupInfo:
    actor_id: int
    cell_id: int
    monster_group_actor: (
        ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor
    )
    move_path: MovementPath


@dataclass
class FighterBehavior(Behavior):
    random_farm_behavior: RandomFarmBehavior
    unload_behavior: UnloadBehavior
    map_move_behavior: MapMoveBehavior
    fight_behavior: FightBehavior
    path_finding: Pathfinding

    def run(self, area_id: int | None, sub_area_id: int | None):
        """random fight in current sub area"""
        self.random_farm_behavior.init_random_farm(area_id, sub_area_id)
        self.random_farm_behavior.additional_weight_by_map_id = (
            self.get_additional_weight_by_map_id()
        )
        self.on_new_map()

    def on_new_map(self):
        if self.game_state.map.map_id in self.random_farm_behavior.map_ids:
            self.attack_enemy()
        else:
            self.run_next_step()

    def run_next_step(self):
        self.random_farm_behavior.start(
            parent=self, callback=self.on_random_farm_behavior_finished
        )

    def on_random_farm_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            if error_code is EdgeError.INVALID_TRANSITION:
                return self.run_next_step()
            raise UnhandledErrorCodeException(error_code)
        self.on_new_map()

    def attack_enemy(self):
        monster_group_info = self.get_next_enemy()
        if monster_group_info is None:
            return self.run_next_step()

        self.run_timer(
            ON_NEW_MAP_BEFORE_ACTION,
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

        self.event_manager.on(
            msg_type=ContextCreationEvent,
            callback=self.on_context_creation_event,
            originator=self,
            once=True,
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
        if self.game_state.inventory.is_full_pods:
            return self.unload_behavior.start(
                parent=self, callback=self.on_unload_behavior_finished
            )
        self.on_new_map()

    def on_unload_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.on_new_map()

    def get_next_enemy(self) -> MonsterGroupInfo | None:
        monster_group_infos: list[MonsterGroupInfo] = []
        for (
            actor_id,
            mp_group,
            monster_group,
        ) in self.game_state.entity.get_monster_groups():
            if not self.is_valid_monster_group(monster_group):
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
                    cell_id=mp_group.cell_id,
                    monster_group_actor=monster_group,
                    move_path=move_path_to_group,
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
    ) -> bool:
        total_group_lvl = 0
        total_group_lvl += monster_group.identification.main_creature.level
        for underling in monster_group.identification.underlings:
            total_group_lvl += underling.level

        return total_group_lvl <= (self.game_state.player.limited_lvl * 1.3 + 3)

    def get_weight_monster_group_info(
        self,
        monster_group_info: MonsterGroupInfo,
    ) -> float:
        duration_move = monster_group_info.move_path.get_total_duration(
            self.game_state.player.is_riding,
            self.game_state.inventory.inventory_weight,
            self.game_state.inventory.weight_max,
        )
        return 1 / (1 + duration_move**2)

    def get_additional_weight_by_map_id(self):
        additional_weight_by_map_id: dict[int, float] = {}
        for map_id in self.random_farm_behavior.map_ids:
            map_pos_data = DataReader().map_pos_by_map_id[map_id]
            m_flags = map_pos_data.m_flags
            if not allow_monster_agression(m_flags):
                additional_weight_by_map_id[map_id] = 0
            else:
                sub_area_lvl = DataReader().sub_area_by_id[map_pos_data.subAreaId].level
                additional_weight_by_map_id[map_id] = 1 / (
                    1 + abs(sub_area_lvl - self.game_state.player.level)
                )
        return additional_weight_by_map_id
