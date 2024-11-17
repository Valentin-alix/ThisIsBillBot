import heapq
from typing import cast

from pydantic import Field, PrivateAttr
from tqdm import tqdm

from D3Mapping.d3_mapping.consts import LIMIT
from D3Mapping.d3_mapping.mapping.services.hungarian.hungarian_solver_service import (
    HungarianSolverService,
)
from D3Mapping.d3_mapping.mapping.services.mapping_enforcement_service import (
    MappingEnforcementService,
)
from D3Mapping.d3_mapping.mapping.services.proto_organization_service import (
    ProtoOrganization,
)
from D3Mapping.d3_mapping.mapping.services.pulp.pulp_solver_service import (
    PulpSolverService,
)
from D3Mapping.d3_mapping.mapping.validators.field_validators import VALIDATORS_ON_FIELD
from D3Mapping.d3_mapping.mapping.validators.global_validators import (
    VALIDATORS_GLOBAL_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.mapping.validators.proto_field_validators import (
    is_parsed_obf_msg,
)
from D3Mapping.d3_mapping.mapping.validators.set_validators import (
    VALIDATORS_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.models.mapping_info import (
    FieldAuditInfo,
    MappingInfo,
    MessageAuditInfo,
    OutputFieldMapping,
    OutputMappingInfo,
)
from D3Mapping.d3_mapping.models.mapping_metrics import MappingMetrics
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import (
    PMessage,
)
from D3Mapping.d3_mapping.utils import get_value_with_len_malus
from src.utils.dataclass_utils import AppModel


class GlobalProtoMapper(AppModel):
    obf_root_namespaces: list[str]
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    verified_msg_by_obf: dict[str, str]
    metrics: MappingMetrics
    pulp_solver_service: PulpSolverService
    hungarian_solver_service: HungarianSolverService
    mapping_enforcement_service: MappingEnforcementService
    added_mapping_by_obf_namespaces: dict[str, MappingInfo]

    msg_mapping_info_by_clear_namespace: dict[str, OutputMappingInfo]

    used_fields: dict[str, list[str]] | None = None

    _clear_name_to_namespace: dict[str, str] | None = PrivateAttr(default=None)
    _validator_priority_cache: dict[str, int] | None = PrivateAttr(default=None)
    _comparison_cache: dict[tuple[str, str, frozenset[str]], MappingInfo] = PrivateAttr(
        default_factory=dict
    )
    _audit_cache: dict[str, tuple[str, int, dict[str, FieldAuditInfo]]] = PrivateAttr(
        default_factory=dict
    )
    audit_by_clear_namespace: dict[str, MessageAuditInfo] = Field(default_factory=dict)

    def _build_indices(self):
        if self._clear_name_to_namespace is None:
            self._clear_name_to_namespace = {
                namespace.split(".")[-1]: namespace
                for namespace in self.clear_struct_by_namespace
            }
        if self._validator_priority_cache is None:
            self._validator_priority_cache = {}
            for obf_namespace, clear_name in self.verified_msg_by_obf.items():
                priority = max(
                    VALIDATORS_ON_SET_FIELDS.get(clear_name, (None, 0))[1],
                    VALIDATORS_GLOBAL_ON_SET_FIELDS.get(clear_name, (None, 0))[1],
                )
                self._validator_priority_cache[obf_namespace] = priority

    def _is_message_used(self, clear_namespace: str) -> bool:
        if self.used_fields is None:
            return True
        return f".{clear_namespace}" in self.used_fields

    def _get_used_fields_for_message(self, clear_namespace: str) -> set[str] | None:
        if self.used_fields is None:
            return None
        return set(self.used_fields.get(f".{clear_namespace}", []))

    def _map_messages(
        self,
        verified_msg_by_obf: dict[str, str],
        desc: str = "",
        check_used: bool = False,
    ) -> dict[str, OutputMappingInfo]:
        self._build_indices()

        sorted_obf_structs = sorted(
            [
                obf_struct
                for obf_struct in self.obf_struct_by_namespace.values()
                if isinstance(obf_struct, PMessage)
                and obf_struct.namespace in verified_msg_by_obf
            ],
            key=lambda obf_struct: self._get_validator_priority(
                obf_struct.namespace, verified_msg_by_obf
            ),
            reverse=True,
        )

        new_mappings: dict[str, OutputMappingInfo] = {}

        for obf_msg in tqdm(sorted_obf_structs, desc=desc or None):
            related_clear_msg_name = verified_msg_by_obf[obf_msg.namespace]
            related_clear_namespace = cast(dict, self._clear_name_to_namespace).get(
                related_clear_msg_name
            )
            if related_clear_namespace is None:
                continue

            if check_used and not self._is_message_used(related_clear_namespace):
                continue

            related_clear_msg = self.clear_struct_by_namespace[related_clear_namespace]
            assert isinstance(related_clear_msg, PMessage)

            mapping_info = self.get_comparison_message(
                related_clear_msg, obf_msg, set()
            )
            self.add_new_msg_mapping(related_clear_msg, obf_msg, mapping_info)

            new_mappings[related_clear_msg.namespace] = (
                self.msg_mapping_info_by_clear_namespace[related_clear_msg.namespace]
            )

        return new_mappings

    def run_mapping(self) -> dict[str, OutputMappingInfo]:
        self._map_messages(self.verified_msg_by_obf, check_used=True)

        print("\n" + "=" * 60)
        print(self.metrics.get_summary())
        print("=" * 60)

        return self.msg_mapping_info_by_clear_namespace

    def map_new_messages(
        self, new_verified_msg_by_obf: dict[str, str]
    ) -> dict[str, OutputMappingInfo]:
        new_mappings = self._map_messages(
            new_verified_msg_by_obf, desc="Mapping new messages"
        )

        print("\n" + "=" * 60)
        print(f"Mapped {len(new_mappings)} new messages")
        print("=" * 60)

        return new_mappings

    def _get_validator_priority(
        self, obf_namespace: str, verified_msg_by_obf: dict[str, str]
    ) -> int:
        if obf_namespace in cast(dict, self._validator_priority_cache):
            return cast(dict, self._validator_priority_cache)[obf_namespace]

        clear_name = verified_msg_by_obf.get(obf_namespace)
        if clear_name is None:
            return 0

        priority = max(
            VALIDATORS_ON_SET_FIELDS.get(clear_name, (None, 0))[1],
            VALIDATORS_GLOBAL_ON_SET_FIELDS.get(clear_name, (None, 0))[1],
        )
        cast(dict, self._validator_priority_cache)[obf_namespace] = priority
        return priority

    def get_comparison_message(
        self,
        clear_msg: PMessage,
        obf_msg: PMessage,
        treated_clear_namespaces: set[str],
    ) -> MappingInfo:
        cache_key = (
            clear_msg.namespace,
            obf_msg.namespace,
            frozenset(treated_clear_namespaces),
        )
        if cache_key in self._comparison_cache:
            return self._comparison_cache[cache_key]

        def _internal_comparison(
            clear_msg: PMessage, obf_msg: PMessage, treated: set[str]
        ) -> MappingInfo:
            treated = treated | {clear_msg.namespace}

            len_clear_elems = len(ProtoOrganization.get_flat_elements(clear_msg))
            len_obf_elems = len(ProtoOrganization.get_flat_elements(obf_msg))

            algorithm: str
            field_audit: dict[str, FieldAuditInfo]

            if (
                clear_msg.name in VALIDATORS_ON_SET_FIELDS
                or clear_msg.name in VALIDATORS_GLOBAL_ON_SET_FIELDS
            ):
                (
                    total_sim,
                    total_reliability,
                    clear_by_obf_field_mapping,
                    field_audit,
                ) = self.pulp_solver_service.get_deep_best_field_mapping_combination(
                    clear_msg,
                    obf_msg,
                    treated,
                    self.get_comparison_message,
                )
                algorithm = "pulp"
            else:
                clear_elem_by_index = ProtoOrganization.get_flat_elements(clear_msg)
                obf_elem_by_index = ProtoOrganization.get_flat_elements(obf_msg)

                (
                    total_sim,
                    total_reliability,
                    clear_by_obf_field_mapping,
                    field_audit,
                ) = self.hungarian_solver_service.get_flat_best_field_mapping_combination(
                    self.get_comparison_message,
                    clear_msg,
                    obf_msg,
                    clear_elem_by_index,
                    obf_elem_by_index,
                    treated,
                )
                algorithm = "hungarian"

            validator_priority = self._get_validator_priority(
                obf_msg.namespace, self.verified_msg_by_obf
            )
            self._audit_cache[clear_msg.namespace] = (
                algorithm,
                validator_priority,
                field_audit,
            )

            if total_reliability == 0:
                return MappingInfo(
                    clear_msg_namespace=clear_msg.namespace,
                    similarity=0,
                    field_mapping={},
                )

            msg_sim = total_sim / total_reliability
            msg_sim = get_value_with_len_malus(msg_sim, len_clear_elems, len_obf_elems)

            return MappingInfo(
                clear_msg_namespace=clear_msg.namespace,
                similarity=msg_sim,
                field_mapping=clear_by_obf_field_mapping,
            )

        result = self.mapping_enforcement_service.enforce_message_comparison(
            clear_msg, obf_msg, _internal_comparison, treated_clear_namespaces
        )
        self._comparison_cache[cache_key] = result
        return result

    def get_most_similar_obf_msg(self, clear_msg: PMessage):
        most_sim_msg_info: tuple[PMessage, MappingInfo] | None = None
        for obf_namespace in tqdm(self.obf_root_namespaces):
            related_obf_struct = self.obf_struct_by_namespace[obf_namespace]
            if not isinstance(related_obf_struct, PMessage):
                continue
            mapping_info = self.get_comparison_message(
                clear_msg, related_obf_struct, set()
            )
            if (
                most_sim_msg_info is None
                or most_sim_msg_info[1].similarity < mapping_info.similarity
            ):
                most_sim_msg_info = (related_obf_struct, mapping_info)

        return most_sim_msg_info

    def get_top_similar_obf_msgs(
        self,
        clear_msg: PMessage,
        n: int = 3,
        min_similarity: float = LIMIT,
        excluded_obf_namespaces: set[str] | None = None,
    ) -> list[tuple[float, str, MappingInfo]]:
        heap: list[tuple[float, str, MappingInfo]] = []
        for obf_namespace in self.obf_root_namespaces:
            if excluded_obf_namespaces and obf_namespace in excluded_obf_namespaces:
                continue
            related_obf_struct = self.obf_struct_by_namespace[obf_namespace]
            if not isinstance(related_obf_struct, PMessage):
                continue
            mapping_info = self.get_comparison_message(
                clear_msg, related_obf_struct, set()
            )
            if mapping_info.similarity >= min_similarity:
                if len(heap) < n:
                    heapq.heappush(
                        heap, (mapping_info.similarity, obf_namespace, mapping_info)
                    )
                elif mapping_info.similarity > heap[0][0]:
                    heapq.heapreplace(
                        heap, (mapping_info.similarity, obf_namespace, mapping_info)
                    )
        return sorted(heap, key=lambda x: x[0], reverse=True)

    def add_new_msg_mapping(
        self, clear_msg: PMessage, obf_msg: PMessage, mapping_info: MappingInfo
    ):
        if clear_msg.namespace in self.msg_mapping_info_by_clear_namespace:
            return

        if (
            clear_msg.name in VALIDATORS_ON_FIELD
            or clear_msg.name in VALIDATORS_ON_SET_FIELDS
            or clear_msg.name in VALIDATORS_GLOBAL_ON_SET_FIELDS
        ) and not is_parsed_obf_msg(obf_msg.namespace):
            print(
                f"<!> Not enough registered msg for {clear_msg.name} with obf_msg {obf_msg.name}"
            )

        self.added_mapping_by_obf_namespaces[obf_msg.namespace] = mapping_info

        used_fields_for_msg = self._get_used_fields_for_message(clear_msg.namespace)

        output_field_mapping: OutputFieldMapping = {}
        filtered_field_audit: dict[str, FieldAuditInfo] = {}

        for _obf_field_name, _mapping_info in mapping_info.field_mapping.items():
            if _mapping_info is None:
                if used_fields_for_msg is None:
                    output_field_mapping[_obf_field_name] = None
                continue

            _sim, _clear_field_name, _sub_mapping_info, _ = _mapping_info

            if (
                used_fields_for_msg is not None
                and _clear_field_name not in used_fields_for_msg
            ):
                continue

            output_field_mapping[_obf_field_name] = _clear_field_name

            if _sub_mapping_info is not None:
                _sub_obf_msg = ProtoOrganization.get_related_struct_from_field_name(
                    self.obf_struct_by_namespace, obf_msg, _obf_field_name
                )
                _sub_clear_msg = self.clear_struct_by_namespace[
                    _sub_mapping_info.clear_msg_namespace
                ]

                assert (
                    type(_sub_obf_msg) is PMessage and type(_sub_clear_msg) is PMessage
                )
                self.add_new_msg_mapping(
                    _sub_clear_msg, _sub_obf_msg, _sub_mapping_info
                )

        self.msg_mapping_info_by_clear_namespace[clear_msg.namespace] = (
            OutputMappingInfo(
                obf_msg_namespace=obf_msg.namespace,
                field_mapping=output_field_mapping,
            )
        )

        if clear_msg.namespace in self._audit_cache:
            algorithm, validator_priority, field_audit = self._audit_cache[
                clear_msg.namespace
            ]

            if used_fields_for_msg is not None:
                filtered_field_audit = {
                    obf: info
                    for obf, info in field_audit.items()
                    if info.matched_clear_field is None
                    or info.matched_clear_field in used_fields_for_msg
                }
            else:
                filtered_field_audit = field_audit

            self.audit_by_clear_namespace[clear_msg.namespace] = MessageAuditInfo(
                similarity=mapping_info.similarity,
                algorithm=algorithm,  # type: ignore
                validator_priority=validator_priority,
                fields=filtered_field_audit,
            )
