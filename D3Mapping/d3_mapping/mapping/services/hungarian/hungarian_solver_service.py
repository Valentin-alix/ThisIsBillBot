from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.optimize import linear_sum_assignment

from D3Mapping.d3_mapping.consts import log_reliability
from D3Mapping.d3_mapping.mapping.services.hungarian.cost_matrix_service import (
    CostMatrixService,
)
from D3Mapping.d3_mapping.models.mapping_info import (
    AlternativeCandidate,
    FieldAuditInfo,
    FieldMapping,
    RejectionReason,
)
from D3Mapping.d3_mapping.models.p_message import PField, PMapField, PMessage


@dataclass
class HungarianSolverResult:
    """Result from Hungarian algorithm solver."""

    total_sim: float
    total_reliability: float
    field_mapping: FieldMapping
    field_audit: dict[str, FieldAuditInfo]


@dataclass
class HungarianSolverService:
    cost_matrix_service: CostMatrixService

    def get_flat_best_field_mapping_combination(
        self,
        compare_msg_func: Callable,
        clear_msg: PMessage,
        obf_msg: PMessage,
        clear_elem_by_index: dict[int, PMapField | PField],
        obf_elem_by_index: dict[int, PMapField | PField],
        treated_clear_namespaces: set[str],
    ):
        result_cost = self.cost_matrix_service.compute(
            clear_msg=clear_msg,
            clear_elem_by_index=clear_elem_by_index,
            obf_msg=obf_msg,
            obf_elem_by_index=obf_elem_by_index,
            treated_namespaces=treated_clear_namespaces,
            compare_msg_func=compare_msg_func,
        )
        result = self.solve(
            obf_elem_by_index=obf_elem_by_index,
            cost_matrix=result_cost.cost_matrix,
            mapping_by_indexes=result_cost.mapping_by_indexes,
            reliability_by_indexes=result_cost.reliability_by_indexes,
            all_comparisons_by_obf_index=result_cost.all_comparisons_by_obf_index,
        )

        return (
            result.total_sim,
            result.total_reliability,
            result.field_mapping,
            result.field_audit,
        )

    def solve(
        self,
        obf_elem_by_index: dict[int, PField | PMapField],
        cost_matrix: np.ndarray,
        mapping_by_indexes: dict,
        reliability_by_indexes: dict[int, dict[int, float]],
        all_comparisons_by_obf_index: dict[
            int, list[tuple[int, str, float, float, RejectionReason | None]]
        ],
    ) -> HungarianSolverResult:
        row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)

        field_mapping: FieldMapping = {}
        field_audit: dict[str, FieldAuditInfo] = {}
        total_reliability = 0.0
        obf_index_to_selected_clear: dict[int, int] = {}

        for i, j in zip(row_ind, col_ind):
            obf_field_name, clear_mapping_info = mapping_by_indexes[(i, j)]
            field_mapping[obf_field_name] = clear_mapping_info
            total_reliability += log_reliability(reliability_by_indexes[i][j])  # type: ignore
            obf_index_to_selected_clear[int(j)] = int(i)

        total_sim = float(cost_matrix[row_ind, col_ind].sum())

        for obf_index, obf_elem in obf_elem_by_index.items():
            if obf_elem.name not in field_mapping:
                field_mapping[obf_elem.name] = None
                alternatives = []
                for (
                    clear_idx,
                    clear_name,
                    sim,
                    rel,
                    rej_reason,
                ) in all_comparisons_by_obf_index[obf_index]:
                    reason = rej_reason if rej_reason else RejectionReason.NOT_SELECTED
                    alternatives.append(
                        AlternativeCandidate(
                            clear_field=clear_name,
                            similarity=sim,
                            rejection_reason=reason,
                            reliability=rel,
                        )
                    )
                field_audit[obf_elem.name] = FieldAuditInfo(
                    matched_clear_field=None,
                    similarity=0,
                    reliability=0,
                    source="calculated",
                    alternatives=alternatives,
                )
            else:
                mapping_tuple = field_mapping[obf_elem.name]
                assert mapping_tuple is not None
                sim, clear_name, _mapping_info, _rejection_reason = mapping_tuple
                selected_clear_idx = obf_index_to_selected_clear[obf_index]
                reliability = reliability_by_indexes[selected_clear_idx][obf_index]

                alternatives = []
                for (
                    clear_idx,
                    alt_clear_name,
                    alt_sim,
                    alt_rel,
                    rej_reason,
                ) in all_comparisons_by_obf_index[obf_index]:
                    if clear_idx == selected_clear_idx:
                        continue
                    reason = rej_reason if rej_reason else RejectionReason.NOT_SELECTED
                    alternatives.append(
                        AlternativeCandidate(
                            clear_field=alt_clear_name,
                            similarity=alt_sim,
                            rejection_reason=reason,
                            reliability=alt_rel,
                        )
                    )

                field_audit[obf_elem.name] = FieldAuditInfo(
                    matched_clear_field=clear_name,
                    similarity=sim,
                    reliability=reliability,
                    source="calculated",
                    alternatives=alternatives,
                )

        return HungarianSolverResult(
            total_sim=total_sim,
            total_reliability=total_reliability,
            field_mapping=field_mapping,
            field_audit=field_audit,
        )
