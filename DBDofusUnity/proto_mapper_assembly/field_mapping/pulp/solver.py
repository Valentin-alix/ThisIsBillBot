from __future__ import annotations

from typing import Protocol

import numpy as np
import pulp

from DBDofusUnity.proto_mapper_assembly.field_mapping.pulp.constraints import (
    GLOBAL_VALIDATOR_FIELD_GROUPS,
    SET_VALIDATOR_FIELD_GROUPS,
    LpConstrainable,
    build_ilp_validator_constraints,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import PreparedFieldMappingContext
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime_data import NormalizedRuntimeInstance


class _LpProblemProto(LpConstrainable, Protocol):
    """Typed protocol covering the pulp.LpProblem surface used in this module."""

    objective: pulp.LpAffineExpression | None

    def solve(self, _solver: object = None, /) -> int: ...

    @property
    def status(self) -> int: ...


def _solve_mapping_problem(problem: _LpProblemProto) -> int:
    return problem.solve(pulp.PULP_CBC_CMD(msg=False))


def solve_field_mapping_ilp(
    *,
    context: PreparedFieldMappingContext,
    similarity_matrix: np.ndarray,
    runtime_instances: tuple[NormalizedRuntimeInstance, ...],
) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Solve the field assignment as an ILP with validator hard constraints.

    Returns (non_obf_indexes, obf_indexes) arrays compatible with the
    linear_sum_assignment return convention, or None when the solver cannot
    find an optimal solution.
    """
    non_obf_fields = context.non_obf.fields
    obf_fields = context.obf.fields

    rows = len(non_obf_fields)
    cols = len(obf_fields)

    mapping_problem: _LpProblemProto = pulp.LpProblem("field_mapping", pulp.LpMaximize)

    lp_variable_by_idxs: dict[tuple[int, int], pulp.LpVariable] = {
        (i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for i in range(rows) for j in range(cols)
    }

    _set_objective(
        problem=mapping_problem,
        lp_variable_by_idxs=lp_variable_by_idxs,
        similarity_matrix=similarity_matrix,
        rows=rows,
        cols=cols,
    )
    _add_bipartite_constraints(
        problem=mapping_problem, lp_variable_by_idxs=lp_variable_by_idxs, rows=rows, cols=cols
    )
    _add_validator_constraints(
        non_obf_message_name=context.non_obf_signature.dump_cs_msg.name,
        non_obf_fields=non_obf_fields,
        obf_fields=obf_fields,
        runtime_instances=runtime_instances,
        lp_variable_by_idxs=lp_variable_by_idxs,
        problem=mapping_problem,
    )

    status = _solve_mapping_problem(mapping_problem)

    if status != pulp.LpStatusOptimal:
        return None

    non_obf_idxs: list[int] = []
    obf_idxs: list[int] = []
    for i in range(rows):
        for j in range(cols):
            val = lp_variable_by_idxs[i, j].varValue
            if val is not None and round(val) == 1:
                non_obf_idxs.append(i)
                obf_idxs.append(j)

    return np.array(non_obf_idxs, dtype=np.intp), np.array(obf_idxs, dtype=np.intp)


def _set_objective(
    *,
    problem: _LpProblemProto,
    lp_variable_by_idxs: dict[tuple[int, int], pulp.LpVariable],
    similarity_matrix: np.ndarray,
    rows: int,
    cols: int,
) -> None:
    terms: list[pulp.LpAffineExpression] = [
        float(similarity_matrix[i, j]) * lp_variable_by_idxs[i, j] for i in range(rows) for j in range(cols)
    ]
    problem.objective = pulp.lpSum(terms)


def _add_bipartite_constraints(
    *,
    problem: _LpProblemProto,
    lp_variable_by_idxs: dict[tuple[int, int], pulp.LpVariable],
    rows: int,
    cols: int,
) -> None:
    for i in range(rows):
        row = pulp.lpSum([lp_variable_by_idxs[i, j] for j in range(cols)])
        problem.addConstraint(row <= 1)
    for j in range(cols):
        col = pulp.lpSum([lp_variable_by_idxs[i, j] for i in range(rows)])
        problem.addConstraint(col <= 1)


def _add_validator_constraints(
    *,
    non_obf_message_name: str,
    non_obf_fields: tuple[DumpCSMessageField, ...],
    obf_fields: tuple[DumpCSMessageField, ...],
    runtime_instances: tuple[NormalizedRuntimeInstance, ...],
    lp_variable_by_idxs: dict[tuple[int, int], pulp.LpVariable],
    problem: LpConstrainable,
) -> None:
    for group in SET_VALIDATOR_FIELD_GROUPS:
        if group.message_short_name != non_obf_message_name:
            continue
        build_ilp_validator_constraints(
            group=group,
            non_obf_fields=non_obf_fields,
            obf_fields=obf_fields,
            runtime_instances=runtime_instances,
            lp_variable_by_idxs=lp_variable_by_idxs,
            problem=problem,
        )
    for group in GLOBAL_VALIDATOR_FIELD_GROUPS:
        if group.message_short_name != non_obf_message_name:
            continue
        build_ilp_validator_constraints(
            group=group,
            non_obf_fields=non_obf_fields,
            obf_fields=obf_fields,
            runtime_instances=runtime_instances,
            lp_variable_by_idxs=lp_variable_by_idxs,
            problem=problem,
        )
