import random
from dataclasses import dataclass, field
from functools import partial

from db_dofus_unity.protos.game.challenge_pb2 import ChallengeBonusChoiceSelectedEvent
from db_dofus_unity.protos.game.common_pb2 import ActorPositionInformation
from db_dofus_unity.protos.game.roleplay_pb2 import AttackMonsterRequest
from src.consts import ON_NEW_MAP_BEFORE_ACTION
from src.core.behaviors.bank.unload_in_bank_behavior import UnloadInBankBehavior
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.repositories.data_reader import DataReader
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState

type MonsterGroupInfo = tuple[
    int,
    int,
    ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    MovementPath,
]


@dataclass
class FighterBehavior(Behavior):
    random_farm_behavior: RandomFarmBehavior
    entity_state: EntityState
    inventory_state: InventoryState
    unload_in_bank_behavior: UnloadInBankBehavior
    map_move_behavior: MapMoveBehavior
    fight_behavior: FightBehavior
    path_finding: Pathfinding
    map_state: MapState
    player_state: PlayerState

    _map_ids: set[int] = field(init=False, default_factory=set)

    def run(self):
        """random fight in current sub area"""
        curr_sub_area = DataReader().map_pos_by_map_id[self.map_state.map_id].subAreaId
        self._map_ids = set(DataReader().sub_area_by_id[curr_sub_area].mapIds.Array)

        self.event_manager.on(
            msg_type=ChallengeBonusChoiceSelectedEvent,
            callback=lambda _: self.fight_behavior.start(
                callback=self.on_fight_behavior_finish, parent=self
            ),
            originator=self,
        )
        self.attack_enemy()

    def on_fight_behavior_finish(self, error_code: str | None):
        if error_code is not None:
            return
        if self.inventory_state.is_full_pods:
            return self.unload_in_bank_behavior.start(
                parent=self, callback=lambda _: self.on_new_map()
            )
        self.on_new_map()

    def on_new_map(self):
        self.run_timer(ON_NEW_MAP_BEFORE_ACTION, self.attack_enemy)

    def attack_enemy(self):
        monster_group_info = self.get_next_enemy()
        if monster_group_info is None:
            return self.random_farm_behavior.start(
                callback=lambda _: self.on_new_map(), parent=self, map_ids=self._map_ids
            )

        actor_id, cell_id, _, move_path = monster_group_info
        self.map_move_behavior.start(
            callback=partial(self.on_moved_to_monster, monster_group_id=actor_id),
            parent=self,
            move_path=move_path,
        )

    def on_moved_to_monster(self, error_code: str, monster_group_id: int):
        if error_code is not None:
            return
        request = AttackMonsterRequest(monster_group_id=monster_group_id)
        self.event_manager.send(request)

    def get_next_enemy(self) -> MonsterGroupInfo | None:
        monster_groups: list[MonsterGroupInfo] = []
        for actor in self.entity_state.actor_by_id.values():
            if not (
                actor.actor_information.HasField("role_play_actor")
                and actor.actor_information.role_play_actor.HasField(
                    "monster_group_actor"
                )
            ) or not self.is_valid_monster_group(
                actor.actor_information.role_play_actor.monster_group_actor
            ):
                continue

            mp_group = MapPoint.from_cell_id(actor.disposition.cell_id)
            move_path_to_group = self.path_finding.find_path(
                self.player_state.map_point,
                {mp_group},
            )
            if move_path_to_group.end != mp_group:
                continue
            monster_groups.append(
                (
                    actor.actor_id,
                    actor.disposition.cell_id,
                    actor.actor_information.role_play_actor.monster_group_actor,
                    move_path_to_group,
                )
            )

        if len(monster_groups) == 0:
            return None

        return random.choices(
            monster_groups,
            [
                self.get_weight_monster_group(monster_group)
                for _, _, monster_group, _ in monster_groups
            ],
        )[0]

    def is_valid_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ) -> bool:
        return True

    def get_weight_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ) -> float:
        return 1
