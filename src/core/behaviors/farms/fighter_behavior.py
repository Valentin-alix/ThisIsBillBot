import random
from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.challenge_pb2 import ChallengeBonusChoiceSelectedEvent
from db_dofus_unity.protos.game.common_pb2 import ActorPositionInformation
from db_dofus_unity.protos.game.roleplay_pb2 import AttackMonsterRequest
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior, EndCode
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.states.entity_state import EntityState


@dataclass
class FighterBehavior(Behavior):
    entity_state: EntityState
    map_move_behavior: MapMoveBehavior
    fight_behavior: FightBehavior

    def run(self):
        self.event_manager.on(
            msg_type=ChallengeBonusChoiceSelectedEvent,
            callback=lambda _: self.fight_behavior.start(callback=None, parent=self),
            originator=self,
        )
        enemy_info = self.choose_enemy()
        if enemy_info is None:
            Logger().info("Did not found enemy in map")
            return
        actor_id, cell_id = enemy_info
        move_path = self.map_move_behavior.get_move_path_to_cell_id(cell_id)
        if move_path is None:
            Logger().info("Did not found path to enemy")
            return
        self.map_move_behavior.start(
            callback=partial(self.on_moved_to_enemy, monster_group_id=actor_id),
            parent=self,
            move_path=move_path,
        )

    def on_moved_to_enemy(self, code: EndCode, monster_group_id: int):
        if code is not EndCode.SUCCESS:
            return
        request = AttackMonsterRequest(monster_group_id=monster_group_id)
        self.event_manager.send(request)

    def choose_enemy(self) -> tuple[int, int] | None:
        monster_group_actors: list[tuple[int, int]] = []
        for actor in self.entity_state.actor_by_id.values():
            if not (
                actor.actor_information.HasField("role_play_actor")
                and actor.actor_information.role_play_actor.HasField(
                    "monster_group_actor"
                )
            ):
                continue
            monster_group_actor: (
                ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor
            ) = actor.actor_information.role_play_actor.monster_group_actor
            monster_group_actors.append((actor.actor_id, actor.disposition.cell_id))

        if not monster_group_actors:
            return None
        return random.choice(monster_group_actors)
