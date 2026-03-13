from dataclasses import dataclass
from enum import StrEnum, auto
from functools import cached_property

from DBDofusUnity.dofus_unity_reader.models.world_graph import Transition, Vertice


class TransitionBanScope(StrEnum):
    MAP_STAY = auto()
    """Re-entering the map may restore access from another zone."""
    SESSION = auto()
    """Invalid world-graph transition; remains banned until reconnect."""


@dataclass(frozen=True)
class BannedTransition:
    vertice_from: Vertice
    vertice_to: Vertice
    transition: Transition
    scope: TransitionBanScope

    @cached_property
    def key(self) -> tuple[Vertice, Vertice, Transition]:
        return (self.vertice_from, self.vertice_to, self.transition)
