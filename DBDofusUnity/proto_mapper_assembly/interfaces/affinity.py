from dataclasses import dataclass
from typing import NamedTuple, Protocol

import numpy as np

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace


@dataclass(frozen=True)
class AffinitySignalInputs:
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
    name: str
    weight: float
    build: AffinityBuilder
    rationale: str
