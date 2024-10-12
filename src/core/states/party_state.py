from dataclasses import dataclass, field

from protos.game.common_pb2 import Character
from src.core.states.state import State


@dataclass
class PartyState(State):
    party_id:int|None = field(init=False, default=None)
    party_member_by_id: dict[int, Character] = field(init=False, default_factory=dict)