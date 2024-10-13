from dataclasses import dataclass, field
from typing import Iterable, cast

from protos.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
    Direction,
    Team,
)
from protos.game.gamemap_pb2 import MapObstacle
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.stats.characteristic import get_stat_by_id
from src.core.states.state import State
from src.interfaces.enums.characteristic_enum import CharacteristicEnum
from src.signals.grid_signals import GridSignals


@dataclass
class FightActor:
    life_point: int
    is_summoned: bool


class ActorByIdDict(dict[int, ActorPositionInformation]):

    def __init__(self, map_point: MapPoint, grid_signals: GridSignals):
        self.map_point = map_point
        self.grid_signals = grid_signals
        super().__init__()

    def __setitem__(self, key: int, value: ActorPositionInformation):
        res = super().__setitem__(key, value)
        self.grid_signals.count_actor_on_cell_id.emit(self.map_point.cell_id, len(self))
        return res

    def __delitem__(self, key: int):
        res = super().__delitem__(key)
        self.grid_signals.count_actor_on_cell_id.emit(self.map_point.cell_id, len(self))
        return res


class ActorByMpDict(dict[MapPoint, ActorByIdDict]):
    def __init__(self, grid_signals: GridSignals):
        self.grid_signals = grid_signals
        super().__init__()

    def __missing__(self, key) -> ActorByIdDict:
        value = ActorByIdDict(map_point=key, grid_signals=self.grid_signals)
        self.__setitem__(key, value)
        return value


class ObstacleByCellIdDict(dict[int, MapObstacle]):
    def __init__(self, grid_signals: GridSignals):
        self.grid_signals = grid_signals
        super().__init__()

    def __setitem__(self, key: int, value: MapObstacle):
        self.grid_signals.set_obstacle_on_cell_id.emit(key, True)
        return super().__setitem__(key, value)

    def __delitem__(self, key: int):
        self.grid_signals.set_obstacle_on_cell_id.emit(key, False)
        return super().__delitem__(key)


type MonsterGroup = tuple[
    int,
    MapPoint,
    ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
]


@dataclass
class EntityState(State):
    grid_signals: GridSignals
    actor_by_id: dict[int, ActorPositionInformation] = field(
        init=False, default_factory=dict
    )
    actor_fight_by_id: dict[int, FightActor] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.obstacle_on_cell_id = ObstacleByCellIdDict(grid_signals=self.grid_signals)
        self.actors_on_mp = ActorByMpDict(grid_signals=self.grid_signals)

    def clear_state(self):
        self.actor_by_id.clear()
        self.actor_fight_by_id.clear()

    def set_map_obstacles(self, map_obstacles: Iterable[MapObstacle]):
        self.clear_obstacles()
        for obstacle in map_obstacles:
            self.obstacle_on_cell_id[obstacle.cell_id] = obstacle

    def clear_obstacles(self):
        for obstacle in list(self.obstacle_on_cell_id.values()):
            del self.obstacle_on_cell_id[obstacle.cell_id]

    def clear_actors(self):
        for actor in list(self.actor_by_id.values()):
            self.remove_actor(actor.actor_id)

    def set_actors(self, actors: Iterable[ActorPositionInformation]):
        old_actor_ids = set((actor.actor_id for actor in self.actor_by_id.values()))
        for actor in actors:
            self.set_actor(actor)
            if actor.actor_id in old_actor_ids:
                old_actor_ids.remove(actor.actor_id)

        # delete old actors
        for old_actor_id in old_actor_ids:
            self.remove_actor(old_actor_id)

    def set_actor(self, actor: ActorPositionInformation, is_summoned: bool = False):
        old_actor = self.actor_by_id.get(actor.actor_id)
        if old_actor:
            del self.actors_on_mp[MapPoint.from_cell_id(old_actor.disposition.cell_id)][
                actor.actor_id
            ]
        self.actor_by_id[actor.actor_id] = actor
        self.actors_on_mp[MapPoint.from_cell_id(actor.disposition.cell_id)][
            actor.actor_id
        ] = actor
        if actor.actor_information.HasField("fighter"):
            target_max_health = get_stat_by_id(
                next(
                    (
                        char
                        for char in actor.actor_information.fighter.stats.characteristics
                        if char.characteristic_id == CharacteristicEnum.LIFE_POINTS
                    )
                )
            )
            self.actor_fight_by_id[actor.actor_id] = FightActor(
                life_point=target_max_health, is_summoned=is_summoned
            )

    def update_actor_disposition(self, actor_id: int, direction: int, cell_id: int):
        related_actor = self.actor_by_id.get(actor_id)
        if not related_actor:
            related_actor = ActorPositionInformation(
                actor_id=actor_id,
                disposition=EntityDisposition(
                    cell_id=cell_id,
                    entity_id=actor_id,
                    direction=cast(Direction, direction),
                ),
            )
            self.actor_by_id[actor_id] = related_actor
        else:
            del self.actors_on_mp[
                MapPoint.from_cell_id(related_actor.disposition.cell_id)
            ][related_actor.actor_id]
            related_actor.disposition.cell_id = cell_id
            related_actor.disposition.direction = direction

        self.actors_on_mp[MapPoint.from_cell_id(related_actor.disposition.cell_id)][
            related_actor.actor_id
        ] = related_actor

    def remove_actor(self, actor_id: int):
        actor = self.actor_by_id.pop(actor_id)
        self.actor_fight_by_id.pop(actor_id, None)
        del self.actors_on_mp[MapPoint.from_cell_id(actor.disposition.cell_id)][
            actor_id
        ]

    def is_entity_actor_on_cell_id(self, cell_id: int) -> bool:
        actors_on_mp = self.actors_on_mp.get(MapPoint.from_cell_id(cell_id))
        return actors_on_mp is not None and len(actors_on_mp) > 0

    def get_enemies(self, team: Team) -> list[ActorPositionInformation]:
        return [
            actor
            for actor in self.actor_by_id.values()
            if actor.actor_information.fighter.spawn_information.team != team
        ]

    def get_allies(self, team: Team) -> list[ActorPositionInformation]:
        return [
            actor
            for actor in self.actor_by_id.values()
            if actor.actor_information.fighter.spawn_information.team == team
        ]

    def get_monster_groups(
        self,
    ) -> list[MonsterGroup]:
        monster_groups: list[MonsterGroup] = []

        for actor in self.actor_by_id.values():
            if not (
                actor.actor_information.HasField("role_play_actor")
                and actor.actor_information.role_play_actor.HasField(
                    "monster_group_actor"
                )
            ):
                continue

            monster_groups.append(
                (
                    actor.actor_id,
                    MapPoint.from_cell_id(actor.disposition.cell_id),
                    actor.actor_information.role_play_actor.monster_group_actor,
                )
            )

        return monster_groups
