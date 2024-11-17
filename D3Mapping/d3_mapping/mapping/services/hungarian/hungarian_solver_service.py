from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.optimize import linear_sum_assignment

from D3Mapping.d3_mapping.consts import log_reliability
from D3Mapping.d3_mapping.mapping.services.field_comparison_service import (
    FieldComparisonService,
)
from D3Mapping.d3_mapping.mapping.services.hungarian.cost_matrix_service import (
    CostMatrixService,
)
from D3Mapping.d3_mapping.mapping.services.proto_reliability_calculator_service import (
    ProtoReliabilityCalculator,
)
from D3Mapping.d3_mapping.models.mapping_info import FieldMapping
from D3Mapping.d3_mapping.models.p_message import PField, PMapField, PMessage


@dataclass
class HungarianSolverResult:
    """Result from Hungarian algorithm solver."""

    total_sim: float
    total_reliability: float
    field_mapping: FieldMapping


@dataclass
class HungarianSolverService:
    reliability_calculator: ProtoReliabilityCalculator
    field_comparison_service: FieldComparisonService
    cost_matrix_service: CostMatrixService
    """Service for solving field mapping using Hungarian algorithm.

    The Hungarian algorithm (also known as Kuhn-Munkres algorithm) solves
    the assignment problem in polynomial time. It's used for flat field
    mapping where we don't need deep constraints.
    """

    def get_flat_best_field_mapping_combination(
        self,
        compare_msg_func: Callable,
        clear_msg: PMessage,
        obf_msg: PMessage,
        clear_elem_by_index: dict[int, PMapField | PField],
        obf_elem_by_index: dict[int, PMapField | PField],
        treated_clear_namespaces: set[str],
    ):
        reliability_by_indexes = (
            self.reliability_calculator.get_flat_reliability_by_indexes(
                clear_msg, obf_msg, treated_clear_namespaces
            )
        )

        result_cost = self.cost_matrix_service.compute(
            clear_msg=clear_msg,
            clear_elem_by_index=clear_elem_by_index,
            obf_msg=obf_msg,
            obf_elem_by_index=obf_elem_by_index,
            reliability_by_indexes=reliability_by_indexes,
            treated_namespaces=treated_clear_namespaces,
            compare_msg_func=compare_msg_func,
        )
        result = self.solve(
            obf_elem_by_index=obf_elem_by_index,
            cost_matrix=result_cost.cost_matrix,
            mapping_by_indexes=result_cost.mapping_by_indexes,
            reliability_by_indexes=reliability_by_indexes,
        )

        return result.total_sim, result.total_reliability, result.field_mapping

    def solve(
        self,
        obf_elem_by_index: dict[int, PField | PMapField],
        cost_matrix: np.ndarray,
        mapping_by_indexes: dict,
        reliability_by_indexes: dict[int, dict[int, float]],
    ) -> HungarianSolverResult:
        """Solve the assignment problem using Hungarian algorithm.

        Args:
            ctx: Comparison context
            clear_elem_by_index: Clear fields indexed
            obf_elem_by_index: Obfuscated fields indexed
            cost_matrix: Similarity matrix (clear x obf)
            mapping_by_indexes: Mapping info by index pairs
            reliability_by_indexes: Reliability matrix

        Returns:
            HungarianSolverResult with best matching
        """
        row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)

        field_mapping: FieldMapping = {}
        total_reliability = 0.0

        for i, j in zip(row_ind, col_ind):
            obf_field_name, clear_mapping_info = mapping_by_indexes[(i, j)]
            field_mapping[obf_field_name] = clear_mapping_info
            total_reliability += log_reliability(reliability_by_indexes[i][j])  # type: ignore

        total_sim = float(cost_matrix[row_ind, col_ind].sum())

        for obf_elem in obf_elem_by_index.values():
            if obf_elem.name not in field_mapping:
                field_mapping[obf_elem.name] = None

        return HungarianSolverResult(
            total_sim=total_sim,
            total_reliability=total_reliability,
            field_mapping=field_mapping,
        )
