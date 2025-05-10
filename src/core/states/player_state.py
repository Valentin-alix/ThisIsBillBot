import dataclasses
from dataclasses import dataclass
from datetime import datetime
from threading import Event

from ankama_launcher_emulator_premium.haapi.haapi import get_game_sub_info_by_login

from src import const
from src.core.signals.player_signals import GameInfoSignals
from src.core.states.area_state import (
    CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER,
)
from src.core.states.state import State


@dataclass
class PlayerState(State):
    game_info_signals: GameInfoSignals
    login: str
    _server_id: int = dataclasses.field(init=False, default=1)
    is_ready_to_play_event: Event = dataclasses.field(init=False)
    _level: int = dataclasses.field(init=False, default=1)
    _character_id: int = dataclasses.field(init=False, default=0)
    _character_name: str = dataclasses.field(init=False, default_factory=str)
    waypoint_map_ids: list[int] = dataclasses.field(
        init=False, default_factory=list[int]
    )
    jobs_lvl_by_id: dict[int, int] = dataclasses.field(
        init=False, default_factory=dict[int, int]
    )

    def __post_init__(self) -> None:
        self.is_ready_to_play_event = Event()

    def clear_state(self):
        CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER.pop(
            (self.server_id, self.character_id), None
        )
        self.server_id = -1
        self.is_ready_to_play_event.clear()
        self.level = 1
        self.character_id = 0
        self.character_name = ""
        self.waypoint_map_ids.clear()
        self.jobs_lvl_by_id.clear()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value: int):
        if value == self._level:
            return
        self._level = value
        if const.DEBUG:
            self.game_info_signals.level.emit(value)

    @property
    def subscription_end_date(self) -> datetime:
        game_sub = get_game_sub_info_by_login(self.login)
        if const.DEBUG:
            self.game_info_signals.subscription_end_date.emit(
                game_sub.end_of_subscribe or const.MIN_DATE
            )
        return game_sub.end_of_subscribe or const.MIN_DATE

    @property
    def is_sub(self) -> bool:
        sub_date = self.subscription_end_date
        return datetime.now(tz=sub_date.tzinfo) < sub_date

    @property
    def is_former_sub(self) -> bool:
        return get_game_sub_info_by_login(self.login).is_former_subscriber

    @property
    def character_id(self):
        return self._character_id

    @character_id.setter
    def character_id(self, value: int):
        self._character_id = value
        if const.DEBUG:
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
    def limited_lvl(self) -> int:
        return min(self.level, 200)

    @property
    def server_id(self) -> int:
        return self._server_id

    @server_id.setter
    def server_id(self, value: int):
        self._server_id = value
        if const.DEBUG:
            self.game_info_signals.server_id.emit(value)
