import dataclasses
from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from src.core.states.state import State


@dataclass
class MapState(State):
    map: MapComplementaryInformationEvent = dataclasses.field(
        init=False, default_factory=MapComplementaryInformationEvent
    )
