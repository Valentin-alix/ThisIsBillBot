import dataclasses
from dataclasses import dataclass, field

from db_dofus_unity.protos.game.common_pb2 import (
    Team,
)
from src.core.states.state import State
from src.signals.player_signals import GameInfoSignals


@dataclass
class FightState(State):
    game_info_signals: GameInfoSignals
    fight_placement_possible_positions: list[int] = field(
        default_factory=list, init=False
    )
    _in_fight: bool = dataclasses.field(init=False, default=False)
    team: Team = dataclasses.field(init=False, default=Team.TEAM_NEUTRAL)

    @property
    def in_fight(self):
        return self._in_fight

    @in_fight.setter
    def in_fight(self, value: bool):
        self._in_fight = value
        self.game_info_signals.in_fight.emit(self._in_fight)
