from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import cast

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    Direction,
    EntityDisposition,
    FightInvisibilityState,
)
from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import MapObstacle
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import CharacteristicEnum
from DBDofusUnity.dofus_unity_reader.game_constants.npc import NpcDialogInfo

from src.core.engine.npcs.npc_lookup import find_npc_ids_by_name
from DBDofusUnity.dofus_unity_reader.grid.map_point import MAP_POINT_BY_CELL_ID, MapPoint

from src import consts
from src.core.engine.fights.stats.characteristic import get_stat_by_id
from src.core.engine.monsters.monster_group import (
    MonsterGroup,
    get_level_monster_group,
    get_monster_groups,
    is_valid_monster_group,
)
from src.core.signals.grid_signals import GridSignals
from src.core.states.player_state import PlayerState
from src.core.states.state import State


class ActorByIdDict(dict[int, ActorPositionInformation]):
    def __init__(self, map_point: MapPoint):
        self.map_point = map_point
        super().__init__()


class ActorByMpDict(dict[MapPoint, ActorByIdDict]):
    def __missing__(self, key: MapPoint) -> ActorByIdDict:
        value = ActorByIdDict(map_point=key)
        self.__setitem__(key, value)
        return value

    def is_entity_actor_on_cell_id(self, cell_id: int) -> bool:
        actors_on_mp = self.get(MapPoint.from_cell_id(cell_id))
        return actors_on_mp is not None and len(actors_on_mp) > 0


@dataclass
class FightActor:
    life_point: int
    is_summoned: bool
    invisibility: FightInvisibilityState = FightInvisibilityState.VISIBLE
    state_id_by_effect_uid: dict[int, int] = field(default_factory=dict[int, int])

    @property
    def state_ids(self) -> frozenset[int]:
        return frozenset(self.state_id_by_effect_uid.values())


@dataclass
class EntityState(State):
    player_state: PlayerState
    grid_signals: GridSignals
    actor_by_id: dict[int, ActorPositionInformation] = field(
        init=False, default_factory=dict[int, ActorPositionInformation]
    )
    actor_fight_by_id: dict[int, FightActor] = field(init=False, default_factory=dict[int, FightActor])
    obstacle_on_cell_id: dict[int, MapObstacle] = field(init=False, default_factory=dict[int, MapObstacle])
    actors_on_mp: ActorByMpDict = field(init=False, default_factory=ActorByMpDict)

    def clear_state(self):
        self.clear_actors()
        self.clear_obstacles()

    def set_map_obstacles(self, map_obstacles: Iterable[MapObstacle]):
        old_cell_ids = set(self.obstacle_on_cell_id.keys())
        new_cell_ids: set[int] = set()

        for obstacle in map_obstacles:
            self.obstacle_on_cell_id[obstacle.cell_id] = obstacle
            new_cell_ids.add(obstacle.cell_id)

        removed_cell_ids = old_cell_ids - new_cell_ids
        for cell_id in removed_cell_ids:
            del self.obstacle_on_cell_id[cell_id]

        batch: list[tuple[int, bool]] = [(cell_id, True) for cell_id in new_cell_ids]
        batch.extend((cell_id, False) for cell_id in removed_cell_ids)
        if batch and consts.DEBUG:
            self.grid_signals.set_obstacle_on_cell_id_batch.emit(batch)

    def clear_obstacles(self):
        if not self.obstacle_on_cell_id:
            return
        batch: list[tuple[int, bool]] = [(cell_id, False) for cell_id in self.obstacle_on_cell_id.keys()]
        self.obstacle_on_cell_id.clear()
        if consts.DEBUG:
            self.grid_signals.set_obstacle_on_cell_id_batch.emit(batch)

    def set_actors(self, actors: Iterable[ActorPositionInformation]):
        old_actor_ids = set(self.actor_by_id.keys())
        affected_cells: set[int] = set()

        for actor in actors:
            if actor.actor_id in self.actor_by_id:
                affected_cells.add(self.actor_by_id[actor.actor_id].disposition.cell_id)
            self._update_actor_data(actor)
            affected_cells.add(actor.disposition.cell_id)
            old_actor_ids.discard(actor.actor_id)

        for actor_id in old_actor_ids:
            if actor_id in self.actor_by_id:
                affected_cells.add(self.actor_by_id[actor_id].disposition.cell_id)
            self._delete_actor_data(actor_id)

        self._emit_actor_counts(affected_cells)

    def set_actor(self, actor: ActorPositionInformation, is_summoned: bool = False):
        affected_cells: set[int] = set()

        if actor.actor_id in self.actor_by_id:
            affected_cells.add(self.actor_by_id[actor.actor_id].disposition.cell_id)

        self._update_actor_data(actor, is_summoned)
        affected_cells.add(actor.disposition.cell_id)

        self._emit_actor_counts(affected_cells)

    def remove_actor(self, actor_id: int):
        if actor_id not in self.actor_by_id:
            return
        cell_id = self.actor_by_id[actor_id].disposition.cell_id
        self._delete_actor_data(actor_id)
        self._emit_actor_counts({cell_id})

    def update_actor_disposition(self, actor_id: int, direction: int, cell_id: int):
        affected_cells: set[int] = {cell_id}

        if actor_id in self.actor_by_id:
            affected_cells.add(self.actor_by_id[actor_id].disposition.cell_id)

        self._remove_actor_on_mp(actor_id)

        actor = self.actor_by_id.get(actor_id)
        if actor:
            actor.disposition.cell_id = cell_id
            actor.disposition.direction = cast(Direction, direction)
        else:
            actor = ActorPositionInformation(
                actor_id=actor_id,
                disposition=EntityDisposition(
                    cell_id=cell_id,
                    entity_id=actor_id,
                    direction=cast(Direction, direction),
                ),
            )
            self.actor_by_id[actor_id] = actor

        self._add_actor_on_mp(actor)
        self._emit_actor_counts(affected_cells)

    def clear_actors(self):
        if not self.actor_by_id:
            return
        affected_cells = {mp.cell_id for mp in self.actors_on_mp.keys()}
        self.actor_by_id.clear()
        self.actor_fight_by_id.clear()
        self.actors_on_mp.clear()
        self._emit_actor_counts(affected_cells, all_zero=True)

    def _update_actor_data(self, actor: ActorPositionInformation, is_summoned: bool = False):
        self._remove_actor_on_mp(actor.actor_id)
        self.actor_by_id[actor.actor_id] = actor
        self._add_actor_on_mp(actor)

        if actor.actor_information.HasField("fighter"):
            life_stat = next(
                (
                    char
                    for char in actor.actor_information.fighter.stats.characteristics
                    if char.characteristic_id == CharacteristicEnum.LIFE_POINTS
                ),
                None,
            )
            if life_stat and actor.actor_id != self.player_state.character_id:
                previous = self.actor_fight_by_id.get(actor.actor_id)
                self.actor_fight_by_id[actor.actor_id] = FightActor(
                    life_point=get_stat_by_id(life_stat),
                    is_summoned=is_summoned,
                    invisibility=(previous.invisibility if previous else FightInvisibilityState.VISIBLE),
                    state_id_by_effect_uid=previous.state_id_by_effect_uid.copy() if previous else {},
                )

    def set_fight_actor_effect(self, target_id: int, uid: int, state_id: int) -> None:
        actor_fight = self.actor_fight_by_id[target_id]
        actor_fight.state_id_by_effect_uid[uid] = state_id

    def remove_fight_actor_effect(self, target_id: int, uid: int) -> None:
        actor_fight = self.actor_fight_by_id[target_id]
        actor_fight.state_id_by_effect_uid.pop(uid, None)

    def set_fight_actor_invisibility(self, target_id: int, invisibility: FightInvisibilityState) -> None:
        actor_fight = self.actor_fight_by_id[target_id]
        actor_fight.invisibility = invisibility

    def _delete_actor_data(self, actor_id: int):
        self.actor_by_id.pop(actor_id, None)
        self.actor_fight_by_id.pop(actor_id, None)
        self._remove_actor_on_mp(actor_id)

    def _add_actor_on_mp(self, actor: ActorPositionInformation):
        cell_id = actor.disposition.cell_id
        if cell_id not in MAP_POINT_BY_CELL_ID:
            self.logger.warning(f"Actor {actor.actor_id} on cell {cell_id} might be invisible")
            return
        mp = MapPoint.from_cell_id(cell_id)
        self.actors_on_mp[mp][actor.actor_id] = actor

    def _remove_actor_on_mp(self, actor_id: int):
        mps_to_remove: list[MapPoint] = []
        for mp, actors in self.actors_on_mp.items():
            if actor_id in actors:
                del actors[actor_id]
                if not actors:
                    mps_to_remove.append(mp)
        for mp in mps_to_remove:
            del self.actors_on_mp[mp]

    def _emit_actor_counts(self, cell_ids: set[int], all_zero: bool = False):
        if not cell_ids or not consts.DEBUG:
            return
        if all_zero:
            batch: list[tuple[int, int]] = [(cell_id, 0) for cell_id in cell_ids]
        else:
            batch = [(cell_id, self._count_actors_on_cell(cell_id)) for cell_id in cell_ids]
        self.grid_signals.count_actor_on_cell_id_batch.emit(batch)

    def _count_actors_on_cell(self, cell_id: int) -> int:
        if cell_id not in MAP_POINT_BY_CELL_ID:
            return 0
        actors = self.actors_on_mp.get(MapPoint.from_cell_id(cell_id))
        return len(actors) if actors else 0

    def get_first_actor_on_cell_id(self, cell_id: int) -> ActorPositionInformation | None:
        actor_on_mp = self.actors_on_mp.get(MapPoint.from_cell_id(cell_id))
        if actor_on_mp:
            return next(iter(actor_on_mp.values()))
        return None

    def get_monster_groups(self) -> list[MonsterGroup]:
        return get_monster_groups(self.actor_by_id)

    def is_valid_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
        monster_group_lvl: int,
        lvl_limit: float,
    ) -> bool:
        return is_valid_monster_group(self.logger, monster_group, monster_group_lvl, lvl_limit)

    def get_level_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ) -> int:
        return get_level_monster_group(monster_group)

    def resolve_npc_id(self, npc_info: NpcDialogInfo) -> int:
        if npc_info.npc_id:
            return npc_info.npc_id
        if npc_info.npc_name is not None:
            candidate_npc_ids = find_npc_ids_by_name(npc_info.npc_name)
            if not candidate_npc_ids:
                raise ValueError(f"No NPC is named {npc_info.npc_name!r}")
            return self.get_npc_id_among(candidate_npc_ids)
        assert npc_info.bones_id
        if npc_info.cell_id is not None:
            return self.get_npc_id_by_cell_and_bones(npc_info.cell_id, npc_info.bones_id)
        return self.get_npc_id_by_bones(npc_info.bones_id)

    def get_npc_id_among(self, candidate_npc_ids: set[int]) -> int:
        found_npc_ids = {
            actor.actor_id
            for actor in self.actor_by_id.values()
            if actor.actor_information.HasField("role_play_actor")
            and actor.actor_information.role_play_actor.HasField("npc_actor")
            and actor.actor_information.role_play_actor.npc_actor.npc_id in candidate_npc_ids
        }
        if not found_npc_ids:
            raise ValueError(f"No NPC among {sorted(candidate_npc_ids)} found on map")
        if len(found_npc_ids) > 1:
            raise ValueError(f"Several NPCs among {sorted(candidate_npc_ids)} found on map")
        return found_npc_ids.pop()

    def get_npc_id_by_cell_and_bones(self, cell_id: int, bones_id: int) -> int:
        mp = MapPoint.from_cell_id(cell_id)
        actors_on_cell = self.actors_on_mp.get(mp)
        if actors_on_cell is None:
            raise ValueError(f"No actors on cell {cell_id}")

        for actor in actors_on_cell.values():
            if actor.actor_information.look.bones_id == bones_id:
                return actor.actor_id

        raise ValueError(f"No NPC with bones_id={bones_id} found on cell {cell_id}")

    def get_npc_id_by_bones(self, bones_id: int) -> int:
        for actor in self.actor_by_id.values():
            if actor.actor_information.look.bones_id == bones_id:
                return actor.actor_id

        raise ValueError(f"No NPC with bones_id={bones_id} found on map")
