from dataclasses import dataclass
from enum import StrEnum, auto

from dofus_unity_reader.models.world_graph import Transition, Vertice


class TransitionBanScope(StrEnum):
    """How long a transition stays out of the world graph search."""

    MAP_STAY = auto()
    """Unreachable from where we stand; entering the map again may put us in the right zone."""
    SESSION = auto()
    """The world graph itself is wrong; only a reconnect re-opens it."""


@dataclass(frozen=True)
class BannedTransition:
    vertice_from: Vertice
    vertice_to: Vertice
    transition: Transition
    scope: TransitionBanScope

    @property
    def key(self) -> tuple[Vertice, Vertice, Transition]:
        return (self.vertice_from, self.vertice_to, self.transition)
