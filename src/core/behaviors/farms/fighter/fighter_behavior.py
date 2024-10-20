import random
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import partial
from typing import Callable

from d3_mapping.resources.protos.game.common_pb2 import ActorPositionInformation
from d3_mapping.resources.protos.game.context_pb2 import ContextCreationEvent
from d3_mapping.resources.protos.game.roleplay_pb2 import AttackMonsterRequest
from data_center.data_reader import DataReader

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.unload_behavior import UnloadBehavior
from src.core.config.timings import ON_NEW_MAP_BEFORE_ACTION
from src.core.logic.flags.map_position_flags import allow_monster_agression
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.monster_gid_enum import MonsterGidEnum


@dataclass
class MonsterGroupInfo:
    actor_id: int
    cell_id: int
    monster_group_actor: (
        ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor
    )
    move_path: MovementPath


@dataclass
class FighterBehavior(Behavior, ABC):
    random_farm_behavior: RandomFarmBehavior
    unload_behavior: UnloadBehavior
    map_move_behavior: MapMoveBehavior
    fight_behavior: FightBehavior
    path_finding: Pathfinding
    sale_hotel_prices_behavior: SaleHotelPricesBehavior

    _level_limit_with_callback: tuple[int, Callable[[], None]] | None = field(
        init=False, default=None
    )

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        level_limit_with_callback: tuple[int, Callable[[], None]] | None,
    ):
        self._level_limit_with_callback = level_limit_with_callback
        self.random_farm_behavior.init_random_farm(
            area_id, sub_area_id, self.get_additional_weight_by_map_id
        )
        self.on_new_map()

    def on_new_map(self):
        if self.game_state.map.map_id in self.random_farm_behavior.map_ids:
            self.logger.info(f"Waiting for all mule to go {self.game_state.map.map_id}")
            self.attack_enemy()
        else:
            self.run_next_step()

    def run_next_step(self):
        self.random_farm_behavior.start(
            parent=self, callback=self.on_random_farm_behavior_finished
        )

    def on_random_farm_behavior_finished(self, error_code: str | None):
        if (
            error_code is not None
            and error_code is not MapChangeError.UNEXPECTED_NEW_MAP
        ):
            if error_code is EdgeError.NO_VALID_TRANSITION:
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
            self.event_manager.clear_listener_by_origin_and_type(
                ContextCreationEvent, self
            )
            self.fight_behavior.start(
                callback=self.on_fight_behavior_finish,
                parent=self,
            )

    def on_fight_behavior_finish(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        if self._level_limit_with_callback is not None:
            level_limit, callback = self._level_limit_with_callback
            if self.game_state.player.level >= level_limit:
                self.finish()
                return callback()

        if self.game_state.inventory.is_full_pods:
            self.on_full_pods()
        else:
            self.on_new_map()

    def on_full_pods(self):
        self.unload_behavior.start(
            parent=self, callback=self.on_unload_behavior_finished
        )

    def on_unload_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        if (
            datetime.now() - self.game_state.sale_hotel.last_time_updated_prices
            > timedelta(hours=1, minutes=30)
        ):
            self.sale_hotel_prices_behavior.start(
                callback=lambda _: self.on_sale_hotel_price_updated_and_unloaded(),
                parent=self,
            )
        else:
            self.on_sale_hotel_price_updated_and_unloaded()

    def on_sale_hotel_price_updated_and_unloaded(self):
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

    def get_level_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ):
        total_group_lvl = 0
        total_group_lvl += monster_group.identification.main_creature.level
        for underling in monster_group.identification.underlings:
            total_group_lvl += underling.level
        return total_group_lvl

    def get_coeff_level(self, level: int):
        return level * 1.3 + 5

    def is_valid_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ) -> bool:
        if monster_group.identification.main_creature.gid == MonsterGidEnum.POUTCH:
            return False
        group_lvl = self.get_coeff_level(self.game_state.player.limited_lvl)
        monster_group_lvl = self.get_level_monster_group(monster_group)
        self.logger.info(
            f"Group lvl : {group_lvl} against monster group lvl : {monster_group_lvl}"
        )
        return monster_group_lvl <= group_lvl

    def get_weight_monster_group_info(
        self,
        monster_group_info: MonsterGroupInfo,
    ) -> float:
        duration_move = MovementPath.get_total_duration(
            monster_group_info.move_path.path,
            self.game_state.inventory.inventory_weight,
            self.game_state.inventory.weight_max,
        )
        return 1 / (1 + duration_move**2)

    def get_additional_weight_by_map_id(self, map_id: int):
        map_pos_data = DataReader().map_pos_by_map_id[map_id]
        m_flags = map_pos_data.m_flags
        if not allow_monster_agression(m_flags):
            weight = 0
        else:
            sub_area_lvl = DataReader().sub_area_by_id[map_pos_data.subAreaId].level
            weight = 1000 / (1 + abs(sub_area_lvl - self.game_state.player.level))
        return weight
