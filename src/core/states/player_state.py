import dataclasses
from dataclasses import dataclass
from datetime import datetime
from threading import Event

from models.world_graph import Vertice
from protos.game.character_pb2 import CharacterLifeStatusEvent
from protos.game.common_pb2 import (
    ServerType,
    CharacterCharacteristic,
    GuildInformation,
)
from src.core.data_center.data_reader import DataReader
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.stats.characteristic import get_stat_by_id
from src.core.logic.world.linked_zone import get_linked_zone_rp
from src.core.states.entity_state import EntityState
from src.core.states.interactive_state import InteractiveState
from src.core.states.map_state import MapState
from src.core.states.state import State
from src.interfaces.models.collectable import Collectable
from src.signals.player_signals import GameInfoSignals


@dataclass
class PlayerState(State):
    game_info_signals: GameInfoSignals
    map_state: MapState
    entity_state: EntityState
    interactive_state: InteractiveState

    is_ready_to_play_event: Event = dataclasses.field(init=False, default_factory=Event)
    life_state: CharacterLifeStatusEvent.LifeStatus = dataclasses.field(
        init=False, default=CharacterLifeStatusEvent.LifeStatus.ALIVE_AND_KICKING
    )
    guild_information: GuildInformation | None = dataclasses.field(
        init=False, default=None
    )
    guild_rank_id: int = dataclasses.field(init=False, default=0)
    life_point: int = dataclasses.field(init=False, default=1)
    max_life_point: int = dataclasses.field(init=False, default=1)
    _breed_id: int = dataclasses.field(init=False, default=0)
    _level: int = dataclasses.field(init=False, default=1)
    _subscription_end_date: datetime = dataclasses.field(
        init=False, default_factory=lambda: datetime(1975, 1, 1)
    )
    _character_id: int = dataclasses.field(init=False, default=0)
    _character_name: str = dataclasses.field(init=False, default_factory=str)

    game_type: ServerType = dataclasses.field(init=False, default=ServerType.UNDEFINED)
    characteristic_by_id: dict[int, CharacterCharacteristic] = dataclasses.field(
        init=False, default_factory=dict
    )
    waypoint_map_ids: list[int] = dataclasses.field(init=False, default_factory=list)
    jobs_lvl_by_id: dict[int, int] = dataclasses.field(init=False, default_factory=dict)
    is_riding: bool = dataclasses.field(init=False, default=False)
    server_id: int = dataclasses.field(init=False, default=0)

    def clear_state(self):
        self.is_ready_to_play_event.clear()
        self.life_state = CharacterLifeStatusEvent.LifeStatus.ALIVE_AND_KICKING
        self.guild_information = None
        self.guild_rank_id = 0
        self.life_point = 1
        self.max_life_point = 1
        self.breed_id = 0
        self.level = 1
        self.subscription_end_date = datetime(1975, 1, 1)
        self.character_id = 0
        self.character_name = ""
        self.game_type = ServerType.UNDEFINED
        self.characteristic_by_id.clear()
        self.waypoint_map_ids.clear()
        self.jobs_lvl_by_id.clear()
        self.is_riding = False

    def get_player_stat_by_id(self, characteristic: int) -> int:
        return get_stat_by_id(self.characteristic_by_id.get(characteristic))

    @property
    def life_percentage(self):
        return self.life_point / self.max_life_point

    @property
    def breed_id(self):
        return self._breed_id

    @breed_id.setter
    def breed_id(self, value: int):
        self._breed_id = value
        self.game_info_signals.breed_id.emit(value)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value: int):
        self._level = value
        self.game_info_signals.level.emit(value)

    @property
    def subscription_end_date(self):
        return self._subscription_end_date

    @subscription_end_date.setter
    def subscription_end_date(self, value: datetime):
        self._subscription_end_date = value
        self.game_info_signals.subscription_end_date.emit(value)

    @property
    def character_id(self):
        return self._character_id

    @character_id.setter
    def character_id(self, value: int):
        self._character_id = value
        self.game_info_signals.character_id.emit(value)

    @property
    def character_name(self):
        return self._character_name

    @character_name.setter
    def character_name(self, value: str):
        self._character_name = value
        self.logger.title = value
        self.game_info_signals.character_name.emit(value)

    @property
    def is_sub(self) -> bool:
        return (
            datetime.now(tz=self.subscription_end_date.tzinfo)
            < self.subscription_end_date
        )

    @property
    def limited_lvl(self) -> int:
        return min(self.level, 200)

    @property
    def map_point(self):
        return MapPoint.from_cell_id(
            self.entity_state.actor_by_id[self.character_id].disposition.cell_id
        )

    def get_farmable_collectables(
        self, excluded_element_ids: set[int] | None = None
    ) -> list[Collectable]:
        farmable_collectables: list[Collectable] = []
        for stated_element in self.interactive_state.stated_element_by_id.values():
            if (
                stated_element.state != 0
                or excluded_element_ids is not None
                and stated_element.element_id in excluded_element_ids
            ):
                continue
            related_interactive = self.interactive_state.interactive_element_by_id.get(
                stated_element.element_id
            )
            if (
                not related_interactive
                or related_interactive.on_current_map is not True
                or len(related_interactive.enabled_skills) == 0
            ):
                continue
            skill = related_interactive.enabled_skills[0]
            data_skill = DataReader().skill_by_id[skill.skill_id]
            if data_skill.gatheredRessourceItem in [-1, 0]:
                continue
            collectable = Collectable(
                map_id=self.map_state.map_id,
                interactive_element=related_interactive,
                skill=skill,
                resource_item_id=data_skill.gatheredRessourceItem,
            )
            if collectable.is_farmable(
                self.jobs_lvl_by_id.get(data_skill.parentJobId, 1)
            ):
                farmable_collectables.append(collectable)

        return farmable_collectables

    @property
    def curr_vertex(self) -> Vertice:
        vertice = WorldGraphReader().get_vertex(
            self.map_state.map_id, self.linked_zone_rp
        )
        if vertice is None:
            potential_vertices = WorldGraphReader().get_vertexes(self.map_state.map_id)
            if len(potential_vertices) == 0:
                raise ValueError(
                    f"no vertice for map {self.map_state.map_id} at {self.map_point}"
                )
            vertice = next(iter(potential_vertices))
        return vertice

    @property
    def linked_zone_rp(self) -> int:
        return get_linked_zone_rp(self.map_state.map_id, self.map_point.cell_id)
