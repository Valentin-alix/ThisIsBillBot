import dataclasses
from dataclasses import dataclass, field

from db_dofus_unity.protos.game.common_pb2 import (
    ActorPositionInformation,
)
from src.core.states.state import State


@dataclass
class FightState(State):
    fight_placement_possible_positions: list[int] = field(
        default_factory=list, init=False
    )
    in_fight: bool = dataclasses.field(init=False, default=False)
    actor_by_id: dict[int, ActorPositionInformation] = field(
        init=False, default_factory=dict
    )
