from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    CharacterCharacteristic,
    ObjectItemInventory,
    SpellModifier,
    SpellModifierType,
)
from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import MapObstacle
from DBDofusUnity.datas.protos.non_obf.game.spell_pb2 import SpellItem
from DBDofusUnity.dofus_unity_reader.data_center.area_info import AreaInfo
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.map_positions_root import MapInformationRootItem
from DBDofusUnity.dofus_unity_reader.models.world_graph import Transition, Vertice

if TYPE_CHECKING:
    from src.core.engine.fights.attack.enemy_data import EnemyData


@dataclass(frozen=True)
class MapMovementContext:
    map_id: int
    in_fight: bool
    obstacle_on_cell_id: Mapping[int, MapObstacle]
    occupied_cell_ids: frozenset[int]


@dataclass(frozen=True)
class CriterionContext:
    is_sub: bool
    player_level: int
    player_limited_level: int
    player_subscription_end_date: datetime
    player_jobs_lvl_by_id: Mapping[int, int]
    player_waypoint_map_ids: frozenset[int]
    player_server_id: int
    player_character_id: int
    map_id: int
    sub_area_id: int
    fight_breed_id: int
    fight_characteristic_by_id: Mapping[int, CharacterCharacteristic]
    inventory_objects_by_uid: Mapping[int, ObjectItemInventory]
    positive_actor_count: int


@dataclass(frozen=True)
class WorldTransitionContext:
    criterion: CriterionContext
    forbidden_edge_transitions: frozenset[tuple[Vertice, Vertice, Transition]]


@dataclass(frozen=True)
class WorldPathContext:
    transition: WorldTransitionContext
    current_map_pos: MapInformationRootItem


@dataclass(frozen=True)
class FightReachableContext:
    map_id: int
    player_map_point: MapPoint
    movement_points: int


@dataclass(frozen=True)
class AttackContext:
    map_id: int
    player_map_point: MapPoint
    player_character_id: int
    player_level: int
    actor_by_id: Mapping[int, ActorPositionInformation]
    enemy_actors: list[ActorPositionInformation]
    enemies_data: list[EnemyData]
    spells: list[SpellItem]
    primary_elem: EffectElement
    modifier_by_type_and_spell_id: dict[tuple[int, SpellModifierType], SpellModifier]
    count_casted_by_spell_id_on_current_turn: dict[int, int]
    cast_turn_by_spell_id: dict[int, int]
    fight_turn: int
    characteristic_by_id: dict[int, CharacterCharacteristic]
    action_points: int
    movement_points: int
    range: int
    life_point: int
    max_life_point: int
    life_percentage: float
    invisible_enemy_cell_ids: frozenset[int]
    breed_id: int
    own_state_ids: frozenset[int]
    own_active_stack_count_by_spell_id: dict[int, int]
    own_active_summon_count: int
    max_active_summon_count: int


@dataclass(frozen=True)
class HarvesterAreaContext:
    player_level: int
    player_waypoint_map_ids: frozenset[int]
    player_is_sub: bool
    player_server_id: int
    player_jobs_lvl_by_id: Mapping[int, int]
    bank_storage_by_gid: Mapping[int, ObjectItemInventory]
    current_area_infos_by_server_and_character: Mapping[tuple[int, int], AreaInfo]
