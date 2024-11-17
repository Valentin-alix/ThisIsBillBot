from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable

import numpy as np

from D3Mapping.d3_mapping.consts import MAX_PARALLEL_WORKERS, log_reliability
from D3Mapping.d3_mapping.mapping.services.field_comparison_service import (
    FieldComparisonService,
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


@dataclass
class CostMatrixService:
    """Service for computing cost matrices for field mapping.

    This service parallelizes the computation of similarity scores
    between all pairs of fields.
    """

    field_comparison_service: FieldComparisonService

    def compute(
        self,
        clear_msg: PMessage,
        clear_elem_by_index: dict[int, PField | PMapField],
        obf_msg: PMessage,
        obf_elem_by_index: dict[int, PField | PMapField],
        reliability_by_indexes: dict[int, dict[int, float]],
        treated_namespaces: set[str],
        compare_msg_func: Callable,
    ) -> CostMatrixResult:
        """Compute cost matrix for all field pairs.

        Args:
            clear_msg: Clear message
            clear_elem_by_index: Indexed clear fields
            obf_msg: Obfuscated message
            obf_elem_by_index: Indexed obfuscated fields
            reliability_by_indexes: Reliability matrix
            treated_namespaces: Treated namespaces
            compare_p_field_func: Function to compare PFields
            compare_map_field_func: Function to compare PMapFields

        Returns:
            CostMatrixResult with cost matrix and mapping info
        """
        cost_matrix = np.zeros((len(clear_elem_by_index), len(obf_elem_by_index)))
        mapping_by_indexes: dict[
            tuple[int, int], tuple[str, tuple[float, str, MappingInfo | None, RejectionReason | None]]
        ] = {}
        all_comparisons_by_obf_index: dict[
            int, list[tuple[int, str, float, float, RejectionReason | None]]
        ] = {i: [] for i in obf_elem_by_index}

        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_WORKERS) as executor:
            futures = {}
            for clear_index, clear_elem in clear_elem_by_index.items():
                for obf_index, obf_elem in obf_elem_by_index.items():
                    future = executor.submit(
                        self.field_comparison_service.compare_elements,
                        compare_msg_func,
                        clear_msg,
                        clear_elem,
                        obf_msg,
                        obf_elem,
                        treated_namespaces,
                    )
                    futures[(clear_index, obf_index)] = future

            for (clear_index, obf_index), future in futures.items():
                result = future.result()
                clear_elem = clear_elem_by_index[clear_index]
                obf_elem = obf_elem_by_index[obf_index]

                reliability = reliability_by_indexes[clear_index][obf_index]
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
        )
