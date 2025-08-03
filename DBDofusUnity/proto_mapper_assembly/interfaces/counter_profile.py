from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cached_property
from math import sqrt


@dataclass(frozen=True)
class CounterProfile:
    """A count multiset with its euclidean norm, so the norm survives across pairings."""

    counts: Mapping[str, int]

    @cached_property
    def norm(self) -> float:
        return sqrt(sum(count * count for count in self.counts.values()))
