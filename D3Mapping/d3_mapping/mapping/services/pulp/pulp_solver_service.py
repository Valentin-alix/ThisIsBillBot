import traceback
from typing import Callable, cast

import pulp
from cachetools import cached
from pydantic import Field

from D3Mapping.d3_mapping.consts import MAX_PULP_ITERATIONS
from D3Mapping.d3_mapping.mapping.debug_messages import (
    PULP_CONVERSION_ERROR,
    format_pulp_timeout,
)
from D3Mapping.d3_mapping.mapping.services.pulp.deep_mapping_data_service import (
    DeepMappingDataService,
)
from D3Mapping.d3_mapping.mapping.services.pulp.pulp_result_converter import (
    PulpResultConverter,
)
from D3Mapping.d3_mapping.mapping.validators.proto_validator import ProtoValidator
from D3Mapping.d3_mapping.models.comparison_context import ComparisonContext
from D3Mapping.d3_mapping.models.mapping_info import (
    AlternativeCandidate,
    FieldAuditInfo,
    FieldMapping,
    RejectionReason,
)
from D3Mapping.d3_mapping.models.mapping_metrics import MappingMetrics
from D3Mapping.d3_mapping.models.p_message import PMessage
from src.utils.dataclass_utils import AppModel

PulpMappingResult = dict[tuple[tuple[str, ...], tuple[str, ...]], float]


class PulpMappingData(AppModel):
    sim_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float]
    reliability_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float]


class PulpModel(AppModel):
    model: pulp.LpProblem
    variables: dict[tuple[tuple[str, ...], tuple[str, ...]], pulp.LpVariable]


class PulpSolverResult(AppModel):
    total_sim: float
    total_reliability: float
    field_mapping: FieldMapping
    field_audit: dict[str, FieldAuditInfo]
    success: bool = True


class PulpSolverService(AppModel):
    metrics: MappingMetrics
    proto_validator: ProtoValidator
    deep_mapping_data_service: DeepMappingDataService
    pulp_result_converter: PulpResultConverter
    failed_combinations: set[tuple[str, str]] = Field(default_factory=set)

    solver: pulp.PULP_CBC_CMD = Field(
        init=False, default_factory=lambda: pulp.PULP_CBC_CMD(msg=False, presolve=True)
    )

    @cached(
        cache={},
        key=lambda _, clear_msg, obf_msg, __, ___: (
            clear_msg.namespace,
            obf_msg.namespace,
        ),
    )
    def get_deep_best_field_mapping_combination(
        self,
        clear_msg: PMessage,
        obf_msg: PMessage,
        treated_clear_namespaces: set[str],
        compare_msg_func: Callable,
    ):
        ctx = ComparisonContext(
            clear_msg=clear_msg,
            obf_msg=obf_msg,
            treated_namespaces=treated_clear_namespaces,
        )

        sim_by_mapping, reliability_by_mapping = self.deep_mapping_data_service.compute(
            None,
            clear_msg,
            None,
            obf_msg,
            treated_clear_namespaces,
            compare_msg_func,
        )

        mapping_data = PulpMappingData(
            sim_by_mapping=sim_by_mapping,
            reliability_by_mapping=reliability_by_mapping,
        )

        result = self.solve(
            ctx=ctx,
            mapping_data=mapping_data,
            converter=self.pulp_result_converter.convert,
            validator=self.proto_validator.is_valid_clear_by_obf_field_mapping,
        )

        return (
            result.total_sim,
            result.total_reliability,
            result.field_mapping,
            result.field_audit,
        )

    def solve(
        self,
        ctx: ComparisonContext,
        mapping_data: PulpMappingData,
        converter,
        validator,
    ) -> PulpSolverResult:
        cache_key = ctx.cache_key

        if cache_key in self.failed_combinations:
            self.metrics.add_pulp_cached_failure()
            return self._empty_result()

        try:
            return self._solve_with_validation(ctx, mapping_data, converter, validator)
        except (PulpTimeoutError, PulpCycleError, Exception) as err:
            self.failed_combinations.add(cache_key)
            if isinstance(err, Exception) and not isinstance(
                err, (PulpTimeoutError, PulpCycleError)
            ):
                print(
                    PULP_CONVERSION_ERROR.format(
                        clear_name=ctx.clear_msg.name, error=str(err)
                    )
                )
                traceback.print_exc()
            return self._empty_result()

    def _solve_with_validation(
        self,
        ctx: ComparisonContext,
        mapping_data: PulpMappingData,
        converter,
        validator,
    ) -> PulpSolverResult:
        pulp_model = self._build_model(mapping_data)
        constraint_history: set[frozenset] = set()

        for _ in range(MAX_PULP_ITERATIONS):
            self.metrics.add_pulp_iteration()
            pulp_model.model.solve(self.solver)

            mapping_result = self._extract_result(
                pulp_model,
                mapping_data.sim_by_mapping,
                mapping_data.reliability_by_mapping,
            )

            if self._is_cycle(mapping_result, constraint_history):
                self.metrics.add_pulp_cycle()
                raise PulpCycleError()

            constraint_history.add(frozenset(mapping_result.keys()))

            field_mapping = converter(ctx.clear_msg, ctx.obf_msg, mapping_result)

            if validator(
                ctx.treated_namespaces, ctx.clear_msg, ctx.obf_msg, field_mapping
            ):
                total_sim = cast(float, pulp.value(pulp_model.model.objective) or 0)
                total_reliability = sum(
                    mapping_data.reliability_by_mapping[pair]
                    for pair in mapping_result.keys()
                )
                field_audit = self._build_field_audit(
                    mapping_result,
                    mapping_data.sim_by_mapping,
                    mapping_data.reliability_by_mapping,
                )
                return PulpSolverResult(
                    total_sim=total_sim,
                    total_reliability=total_reliability,
                    field_mapping=field_mapping,
                    field_audit=field_audit,
                )

            self.metrics.add_validation_failure()
            self._add_exclusion_constraint(pulp_model, set(mapping_result.keys()))

        self.metrics.add_pulp_timeout()
        print(
            format_pulp_timeout(
                ctx.clear_msg.name, ctx.obf_msg.name, len(constraint_history)
            )
        )
        raise PulpTimeoutError()

    def _build_model(self, mapping_data: PulpMappingData) -> PulpModel:
        model = pulp.LpProblem("BestPathMapping", pulp.LpMaximize)
        variables: dict[tuple[tuple[str, ...], tuple[str, ...]], pulp.LpVariable] = {}
        for clear_path, obf_path in mapping_data.sim_by_mapping:
            var_name = f"map_{'_'.join(clear_path)}__{'_'.join(obf_path)}"
            variables[(clear_path, obf_path)] = pulp.LpVariable(var_name, cat="Binary")

        for (clear_path, obf_path), var in variables.items():
            for i in range(1, len(clear_path)):
                parent_var = variables[(clear_path[:i], obf_path[:i])]
                model += (
                    var <= parent_var,
                    f"parent_constraint_{var.name}_le_{parent_var.name}",
                )

        pairs_by_path: dict[tuple[str, ...], list] = {}
        for clear_path, obf_path in variables.keys():
            pairs_by_path.setdefault(clear_path, []).append((clear_path, obf_path))
            pairs_by_path.setdefault(obf_path, []).append((clear_path, obf_path))
        for pairs in pairs_by_path.values():
            model += pulp.lpSum(variables[pair] for pair in pairs) <= 1

        model += pulp.lpSum(
            mapping_data.sim_by_mapping[(clear_path, obf_path)]
            * variables[(clear_path, obf_path)]
            for (clear_path, obf_path) in mapping_data.sim_by_mapping
        )

        return PulpModel(model=model, variables=variables)

    def _add_exclusion_constraint(self, pulp_model: PulpModel, failed_mapping: set):
        pulp_model.model += (
            pulp.lpSum(pulp_model.variables[pair] for pair in failed_mapping)
            <= len(failed_mapping) - 1
        )

    def _extract_result(
        self,
        pulp_model: PulpModel,
        sim_by_mapping: dict,
        reliability_by_mapping: dict,
    ) -> PulpMappingResult:
        result = {}
        for clear_path, obf_path in sim_by_mapping:
            if pulp.value(pulp_model.variables[(clear_path, obf_path)]) == 1:
                result[(clear_path, obf_path)] = (
                    sim_by_mapping[(clear_path, obf_path)]
                    / reliability_by_mapping[(clear_path, obf_path)]
                )
        return result

    def _is_cycle(
        self, mapping_result: PulpMappingResult, history: set[frozenset]
    ) -> bool:
        current = frozenset(mapping_result.keys())
        return current in history

    def _empty_result(self) -> PulpSolverResult:
        return PulpSolverResult(
            total_sim=0,
            total_reliability=1,
            field_mapping={},
            field_audit={},
            success=False,
        )

    def _build_field_audit(
        self,
        selected_mappings: PulpMappingResult,
        sim_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float],
        reliability_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float],
    ) -> dict[str, FieldAuditInfo]:
        field_audit: dict[str, FieldAuditInfo] = {}

        selected_by_obf: dict[str, tuple[str, float, float]] = {}
        for (clear_path, obf_path), sim in selected_mappings.items():
            if len(obf_path) == 1:
                obf_field = obf_path[0]
                clear_field = clear_path[0]
                reliability = reliability_by_mapping.get((clear_path, obf_path), 0)
                selected_by_obf[obf_field] = (clear_field, sim, reliability)

        all_alternatives_by_obf: dict[str, list[tuple[str, float, float]]] = {}
        for (clear_path, obf_path), weighted_sim in sim_by_mapping.items():
            if len(obf_path) == 1:
                obf_field = obf_path[0]
                clear_field = clear_path[0]
                reliability = reliability_by_mapping.get((clear_path, obf_path), 1)
                sim = weighted_sim / reliability if reliability > 0 else 0
                if obf_field not in all_alternatives_by_obf:
                    all_alternatives_by_obf[obf_field] = []
                all_alternatives_by_obf[obf_field].append(
                    (clear_field, sim, reliability)
                )

        for obf_field, alternatives in all_alternatives_by_obf.items():
            if obf_field in selected_by_obf:
                selected_clear, selected_sim, selected_rel = selected_by_obf[obf_field]
                alt_candidates = [
                    AlternativeCandidate(
                        clear_field=alt_clear,
                        similarity=alt_sim,
                        rejection_reason=RejectionReason.NOT_SELECTED,
                        reliability=alt_reliability,
                    )
                    for alt_clear, alt_sim, alt_reliability in alternatives
                    if alt_clear != selected_clear
                ]
                field_audit[obf_field] = FieldAuditInfo(
                    matched_clear_field=selected_clear,
                    similarity=selected_sim,
                    reliability=selected_rel,
                    source="calculated",
                    alternatives=alt_candidates,
                )
            else:
                alt_candidates = [
                    AlternativeCandidate(
                        clear_field=alt_clear,
                        similarity=alt_sim,
                        rejection_reason=RejectionReason.NOT_SELECTED,
                        reliability=alt_reliability,
                    )
                    for alt_clear, alt_sim, alt_reliability in alternatives
                ]
                field_audit[obf_field] = FieldAuditInfo(
                    matched_clear_field=None,
                    similarity=0,
                    reliability=0,
                    source="calculated",
                    alternatives=alt_candidates,
                )

        return field_audit


class PulpTimeoutError(Exception):
    pass


class PulpCycleError(Exception):
    pass
