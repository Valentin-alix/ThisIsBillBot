from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

import numpy as np

from D3Mapping.d3_mapping.consts import BASE_RELIABILITY, log_reliability
from D3Mapping.d3_mapping.mapping.services.field_comparison_service import (
    FieldComparisonService,
)
from D3Mapping.d3_mapping.mapping.services.proto_reliability_calculator_service import (
    ProtoReliabilityCalculator,
)
from D3Mapping.d3_mapping.models.mapping_info import MappingInfo, RejectionReason
from D3Mapping.d3_mapping.models.p_message import PField, PMapField, PMessage


@dataclass
class CostMatrixResult:
    """Result of cost matrix computation."""

    cost_matrix: np.ndarray
    mapping_by_indexes: dict[
        tuple[int, int], tuple[str, tuple[float, str, MappingInfo | None, RejectionReason | None]]
    ]
    all_comparisons_by_obf_index: dict[
        int, list[tuple[int, str, float, float, RejectionReason | None]]
    ]
    reliability_by_indexes: dict[int, dict[int, float]]


@dataclass
class CostMatrixService:
    field_comparison_service: FieldComparisonService
    reliability_calculator: ProtoReliabilityCalculator

    def compute(
        self,
        clear_msg: PMessage,
        clear_elem_by_index: dict[int, PField | PMapField],
        obf_msg: PMessage,
        obf_elem_by_index: dict[int, PField | PMapField],
        treated_namespaces: set[str],
        compare_msg_func: Callable,
    ) -> CostMatrixResult:
        cost_matrix = np.zeros((len(clear_elem_by_index), len(obf_elem_by_index)))
        mapping_by_indexes: dict[
            tuple[int, int], tuple[str, tuple[float, str, MappingInfo | None, RejectionReason | None]]
        ] = {}
        all_comparisons_by_obf_index: dict[
            int, list[tuple[int, str, float, float, RejectionReason | None]]
        ] = {i: [] for i in obf_elem_by_index}
        reliability_by_indexes: dict[int, dict[int, float]] = defaultdict(dict)

        for clear_index, clear_elem in clear_elem_by_index.items():
            for obf_index, obf_elem in obf_elem_by_index.items():
                result = self.field_comparison_service.compare_elements(
                    compare_msg_func,
                    clear_msg,
                    clear_elem,
                    obf_msg,
                    obf_elem,
                    treated_namespaces,
                )

                if type(clear_elem) is PField and type(obf_elem) is PField:
                    reliability = self.reliability_calculator.get_reliability_p_clear_field(
                        clear_msg, clear_elem, obf_msg, obf_elem, treated_namespaces
                    )
                elif type(clear_elem) is PMapField and type(obf_elem) is PMapField:
                    reliability = self.reliability_calculator.get_reliability_clear_map_field(
                        clear_msg, clear_elem, obf_msg, obf_elem, treated_namespaces
                    )
                else:
                    reliability = BASE_RELIABILITY

                reliability_by_indexes[clear_index][obf_index] = reliability
                weighted_sim = result.similarity * log_reliability(reliability)

                cost_matrix[clear_index][obf_index] = weighted_sim
                mapping_by_indexes[(clear_index, obf_index)] = (
                    obf_elem.name,
                    (result.similarity, clear_elem.name, result.mapping_info, result.rejection_reason),
                )
                all_comparisons_by_obf_index[obf_index].append(
                    (clear_index, clear_elem.name, result.similarity, reliability, result.rejection_reason)
                )

        return CostMatrixResult(
            cost_matrix=cost_matrix,
            mapping_by_indexes=mapping_by_indexes,
            all_comparisons_by_obf_index=all_comparisons_by_obf_index,
            reliability_by_indexes=dict(reliability_by_indexes),
        )
