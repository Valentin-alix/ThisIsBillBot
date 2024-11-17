from dataclasses import dataclass, field
from typing import Callable

from D3Mapping.d3_mapping.consts import log_reliability
from D3Mapping.d3_mapping.mapping.services.field_comparison_service import (
    FieldComparisonService,
)
from D3Mapping.d3_mapping.mapping.services.proto_organization_service import (
    ProtoOrganization,
)
from D3Mapping.d3_mapping.mapping.services.proto_reliability_calculator_service import (
    ProtoReliabilityCalculator,
)
from D3Mapping.d3_mapping.mapping.validators.field_validators import (
    VALIDATORS_ON_FIELD,
)
from D3Mapping.d3_mapping.mapping.validators.proto_field_validators import (
    is_condition_respected,
)
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import PField, PMapField, PMessage

PulpMappingStruct = dict[tuple[tuple[str, ...], tuple[str, ...]], float]


@dataclass
class DeepMappingDataService:
    """Service for computing deep mapping similarity data for PuLP optimization."""

    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    reliability_calculator: ProtoReliabilityCalculator
    field_comparison_service: FieldComparisonService

    _compute_cache: dict[
        tuple[str, str, frozenset[str]],
        tuple[PulpMappingStruct, dict[tuple[tuple[str, ...], tuple[str, ...]], float]]
    ] = field(default_factory=dict)

    def compute(
        self,
        clear_prefix: tuple[str, ...] | None,
        clear_msg: PMessage,
        obf_prefix: tuple[str, ...] | None,
        obf_msg: PMessage,
        treated_clear_namespaces: set[str],
        compare_msg_func: Callable,
    ) -> tuple[PulpMappingStruct, dict[tuple[tuple[str, ...], tuple[str, ...]], float]]:
        """Compute similarity and reliability mappings for deep field mapping.

        This function recursively processes all fields in the messages and their
        nested sub-messages, building a complete mapping structure for PuLP optimization.

        Args:
            clear_prefix: Path prefix for clear message fields
            clear_msg: Clear message to analyze
            obf_prefix: Path prefix for obfuscated message fields
            obf_msg: Obfuscated message to analyze
            treated_clear_namespaces: Set of already processed namespaces

        Returns:
            Tuple of (sim_by_mapping, reliability_by_mapping)
        """
        cache_key = (
            clear_msg.namespace,
            obf_msg.namespace,
            frozenset(treated_clear_namespaces)
        )
        if cache_key in self._compute_cache:
            cached_sim, cached_rel = self._compute_cache[cache_key]
            if clear_prefix is None and obf_prefix is None:
                return cached_sim, cached_rel

        sim_by_mapping: PulpMappingStruct = {}
        reliability_by_mapping: dict[
            tuple[tuple[str, ...], tuple[str, ...]], float
        ] = {}

        clear_elements = ProtoOrganization.get_flat_elements(clear_msg)
        obf_elements = ProtoOrganization.get_flat_elements(obf_msg)
        validators_cache = VALIDATORS_ON_FIELD.get(clear_msg.name, {})

        for clear_elem in clear_elements.values():
            for obf_elem in obf_elements.values():
                if type(clear_elem) is PField and type(obf_elem) is PField:
                    if validators_cache:
                        related_field_validators = validators_cache.get(clear_elem.name)
                        if related_field_validators:
                            is_respected = is_condition_respected(
                                obf_msg.namespace,
                                obf_elem.name,
                                related_field_validators,
                            )
                            if not is_respected:
                                continue

                    cost, mapping_info, _ = self.field_comparison_service.compare_p_field(
                        compare_msg_func,
                        clear_msg,
                        clear_elem,
                        obf_msg,
                        obf_elem,
                        treated_clear_namespaces,
                    )
                    reliability_field = (
                        self.reliability_calculator.get_reliability_p_clear_field(
                            clear_msg, clear_elem, obf_msg, obf_elem, set()
                        )
                    )

                elif type(clear_elem) is PMapField and type(obf_elem) is PMapField:
                    cost, mapping_info, _ = (
                        self.field_comparison_service.compare_map_fields(
                            compare_msg_func,
                            clear_msg,
                            clear_elem,
                            obf_msg,
                            obf_elem,
                            treated_clear_namespaces,
                        )
                    )
                    reliability_field = (
                        self.reliability_calculator.get_reliability_clear_map_field(
                            clear_msg, clear_elem, obf_msg, obf_elem, set()
                        )
                    )
                else:
                    cost = 0
                    mapping_info = None
                    reliability_field = 0

                if cost == 0:
                    continue

                mapping_key = (
                    (
                        *(clear_prefix or []),
                        clear_elem.name,
                    ),
                    (
                        *(obf_prefix or []),
                        obf_elem.name,
                    ),
                )
                reliability_by_mapping[mapping_key] = log_reliability(reliability_field)
                cost *= reliability_by_mapping[mapping_key]
                sim_by_mapping[mapping_key] = cost

                if mapping_info is not None:
                    # it is nested
                    sub_clear_struct = (
                        ProtoOrganization.get_related_struct_from_field_name(
                            self.clear_struct_by_namespace, clear_msg, clear_elem.name
                        )
                    )
                    assert type(sub_clear_struct) is PMessage

                    if sub_clear_struct.namespace in treated_clear_namespaces:
                        continue

                    sub_obf_struct = (
                        ProtoOrganization.get_related_struct_from_field_name(
                            self.obf_struct_by_namespace, obf_msg, obf_elem.name
                        )
                    )
                    assert type(sub_obf_struct) is PMessage
                    sub_sim_by_mapping, sub_reliability_by_mapping = self.compute(
                        clear_prefix + (clear_elem.name,)
                        if clear_prefix is not None
                        else (clear_elem.name,),
                        sub_clear_struct,
                        obf_prefix + (obf_elem.name,)
                        if obf_prefix is not None
                        else (obf_elem.name,),
                        sub_obf_struct,
                        treated_clear_namespaces | {sub_clear_struct.namespace},
                        compare_msg_func=compare_msg_func,
                    )
                    sim_by_mapping |= sub_sim_by_mapping
                    reliability_by_mapping |= sub_reliability_by_mapping

        if clear_prefix is None and obf_prefix is None:
            self._compute_cache[cache_key] = (sim_by_mapping, reliability_by_mapping)

        return sim_by_mapping, reliability_by_mapping
