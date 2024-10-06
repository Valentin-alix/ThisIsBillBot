from dataclasses import dataclass, field
from typing import Iterable, cast

from db_dofus_unity.protos.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
    Direction,
    Team,
)
from db_dofus_unity.protos.game.gamemap_pb2 import MapObstacle
from src.core.states.state import State
from src.signals.grid_signals import GridSignals


class ActorByIdDict(dict[int, ActorPositionInformation]):

    def __init__(self, cell_id: int, grid_signals: GridSignals):
        self.cell_id = cell_id
        self.grid_signals = grid_signals
        super().__init__()

    def __setitem__(self, key: int, value: ActorPositionInformation):
        res = super().__setitem__(key, value)
        self.grid_signals.count_actor_on_cell_id.emit(self.cell_id, len(self))
        return res

    def __delitem__(self, key: int):
        res = super().__delitem__(key)
        self.grid_signals.count_actor_on_cell_id.emit(self.cell_id, len(self))
        return res


class ActorByCellIdDict(dict[int, ActorByIdDict]):
    def __init__(self, grid_signals: GridSignals):
        self.grid_signals = grid_signals
        super().__init__()

    def __missing__(self, key) -> ActorByIdDict:
        value = ActorByIdDict(cell_id=key, grid_signals=self.grid_signals)
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


@dataclass
class EntityState(State):
    grid_signals: GridSignals
    actor_by_id: dict[int, ActorPositionInformation] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self):
        self.obstacle_on_cell_id = ObstacleByCellIdDict(grid_signals=self.grid_signals)
        self.actors_on_cell_id = ActorByCellIdDict(grid_signals=self.grid_signals)

    def set_map_obstacles(self, map_obstacles: Iterable[MapObstacle]):
        self.clear_obstacles()
        for obstacle in map_obstacles:
            self.obstacle_on_cell_id[obstacle.cell_id] = obstacle

    def clear_obstacles(self):
        for obstacle in list(self.obstacle_on_cell_id.values()):
            del self.obstacle_on_cell_id[obstacle.cell_id]

    def clear_actors(self):
        for actor in list(self.actor_by_id.values()):
            del self.actors_on_cell_id[actor.disposition.cell_id][actor.actor_id]
            del self.actor_by_id[actor.actor_id]

    def set_actors(self, actors: Iterable[ActorPositionInformation]):
        self.clear_actors()
        for actor in actors:
            self.actors_on_cell_id[actor.disposition.cell_id][actor.actor_id] = actor
            self.actor_by_id[actor.actor_id] = actor

    def set_actor(self, actor: ActorPositionInformation):
        if actor.actor_id in self.actor_by_id:
            self.remove_actor(actor.actor_id)
        self.actor_by_id[actor.actor_id] = actor
        self.actors_on_cell_id[actor.disposition.cell_id][actor.actor_id] = actor

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
            self.set_actor(related_actor)

        del self.actors_on_cell_id[related_actor.disposition.cell_id][actor_id]
        related_actor.disposition.cell_id = cell_id
        related_actor.disposition.direction = direction
        self.actors_on_cell_id[related_actor.disposition.cell_id][
            actor_id
        ] = related_actor

    def remove_actor(self, actor_id: int):
        actor = self.actor_by_id.pop(actor_id)
        del self.actors_on_cell_id[actor.disposition.cell_id][actor_id]

    def is_entity_actor_on_cell_id(self, cell_id: int) -> bool:
        return cell_id in self.actors_on_cell_id

    def get_enemies(self, team: Team) -> list[ActorPositionInformation]:
        return [
            actor
            for actor in self.actor_by_id.values()
            if actor.actor_information.fighter.spawn_information.team != team
        ]
