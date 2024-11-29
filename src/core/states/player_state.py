import dataclasses
from dataclasses import dataclass
from datetime import datetime
from threading import Event

from src.core.signals.player_signals import GameInfoSignals
from src.core.states.area_state import (
    CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER,
)
from src.core.states.state import State


@dataclass
class PlayerState(State):
    game_info_signals: GameInfoSignals
    _server_id: int = dataclasses.field(init=False, default=1)
    is_ready_to_play_event: Event = dataclasses.field(init=False)
    _level: int = dataclasses.field(init=False, default=1)
    _subscription_end_date: datetime = dataclasses.field(
        init=False, default_factory=lambda: datetime(1975, 1, 1)
    )
    _character_id: int = dataclasses.field(init=False, default=0)
    _character_name: str = dataclasses.field(init=False, default_factory=str)
    waypoint_map_ids: list[int] = dataclasses.field(init=False)
    jobs_lvl_by_id: dict[int, int] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.is_ready_to_play_event = Event()
        waypoint_map_ids: list[int] = []
        jobs_lvl_by_id: dict[int, int] = {}
        self.waypoint_map_ids = waypoint_map_ids
        self.jobs_lvl_by_id = jobs_lvl_by_id

    def clear_state(self):
        CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER.pop(
            (self.server_id, self.character_id), None
        )
        self.server_id = -1
        self.is_ready_to_play_event.clear()
        self.level = 1
        self.subscription_end_date = datetime(1975, 1, 1)
        self.character_id = 0
        self.character_name = ""
        self.waypoint_map_ids.clear()
        self.jobs_lvl_by_id.clear()

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
    def server_id(self) -> int:
        return self._server_id

    @server_id.setter
    def server_id(self, value: int):
        self._server_id = value
        self.game_info_signals.server_id.emit(value)
