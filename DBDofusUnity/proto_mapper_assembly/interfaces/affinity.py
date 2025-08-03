from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Protocol

import numpy as np

from proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument
from proto_mapper_assembly.interfaces.matching import MatchingWorkspace


@dataclass(frozen=True)
class AffinitySignalInputs:
    """
    Everything a corpus-level signal is allowed to look at.

    Passed as one object rather than as parameters so that a signal reading only part of it — the
    callee affinity never opens ``base_scores_matrix`` — is simply not reading a field, instead of
    carrying an argument it has to ignore.
    """

    workspace: MatchingWorkspace
    base_scores_matrix: np.ndarray
    obf_access_trace: AccessTraceDocument
    non_obf_access_trace: AccessTraceDocument


class AffinityResult(NamedTuple):
    affinity_matrix: np.ndarray
    applicable_mask: np.ndarray


class AffinityBuilder(Protocol):
    def __call__(self, signal_inputs: AffinitySignalInputs, /) -> AffinityResult: ...


@dataclass(frozen=True)
class MaskedAffinitySignal:
    """One entry of the blend table: what it is worth, how it is computed, and why it exists."""

    name: str
    weight: float
    build: AffinityBuilder
    rationale: str
