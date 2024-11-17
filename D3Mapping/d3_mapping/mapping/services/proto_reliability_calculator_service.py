from collections import defaultdict

import numpy as np
from proto_schema_parser import FieldCardinality
from pydantic import BaseModel
from scipy.optimize import linear_sum_assignment

from D3Mapping.d3_mapping.consts import (
    BASE_RELIABILITY,
    EXTRA_RELIABILITY_ENUM,
    EXTRA_RELIABILITY_MAP,
    EXTRA_RELIABILITY_MESSAGE,
    EXTRA_RELIABILITY_WITH_VALIDATOR,
    PROTO_BASE_FIELDS,
    RELIABILITY_BY_PROTO_BASE_FIELDS,
    log_reliability,
)
from D3Mapping.d3_mapping.mapping.services.proto_organization_service import (
    ProtoOrganization,
)
from D3Mapping.d3_mapping.mapping.validators.field_validators import VALIDATORS_ON_FIELD
from D3Mapping.d3_mapping.mapping.validators.global_validators import (
    VALIDATORS_GLOBAL_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.mapping.validators.proto_field_validators import (
    get_count_defined_msg_field_values,
    is_parsed_obf_msg,
)
from D3Mapping.d3_mapping.mapping.validators.set_validators import (
    VALIDATORS_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import PField, PMapField, PMessage


class ProtoReliabilityCalculator(BaseModel):
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]

    reliability_by_clear_namespace_with_obf_namespace: dict[tuple[str, str], float] = {}
    verified_obf_msg_name_by_clear_msg_name: dict[str, str]

    def get_flat_reliability_by_indexes(
        self, clear_msg: PMessage, obf_msg: PMessage, treated_msg_namespaces: set[str]
    ) -> dict[int, dict[int, float]]:
        """get reliability by field  with the total reliability"""
        reliability_by_indexes: dict[int, dict[int, float]] = defaultdict(dict)

        clear_elem_by_index = ProtoOrganization.get_flat_elements(clear_msg)
        obf_elem_by_index = ProtoOrganization.get_flat_elements(obf_msg)

        for clear_index, _clear_elem in clear_elem_by_index.items():
            for obf_index, _obf_elem in obf_elem_by_index.items():
                if type(_clear_elem) is PField and type(_obf_elem) is PField:
                    reliability_by_indexes[clear_index][obf_index] = (
                        self.get_reliability_p_clear_field(
                            clear_msg,
                            _clear_elem,
                            obf_msg,
                            _obf_elem,
                            treated_msg_namespaces,
                        )
                    )
                elif type(_clear_elem) is PMapField and type(_obf_elem) is PMapField:
                    reliability_by_indexes[clear_index][obf_index] = (
                        self.get_reliability_clear_map_field(
                            clear_msg,
                            _clear_elem,
                            obf_msg,
                            _obf_elem,
                            treated_msg_namespaces,
                        )
                    )
                else:
                    reliability_by_indexes[clear_index][obf_index] = BASE_RELIABILITY

        return reliability_by_indexes

    def get_reliability_clear_enum(self, enum: PEnum) -> float:
        return len(enum.elements) + EXTRA_RELIABILITY_ENUM

    def get_reliability_clear_message(
        self, clear_msg: PMessage, obf_msg: PMessage, treated_msg_namespaces: set[str]
    ) -> float:
        if (
            clear_msg.namespace,
            obf_msg.namespace,
        ) in self.reliability_by_clear_namespace_with_obf_namespace:
            return self.reliability_by_clear_namespace_with_obf_namespace[
                (clear_msg.namespace, obf_msg.namespace)
            ]

        if (
            clear_msg.name in self.verified_obf_msg_name_by_clear_msg_name
            and self.verified_obf_msg_name_by_clear_msg_name[clear_msg.name]
            == obf_msg.name
        ):
            return 999

        count_validator = 0
        if clear_msg.name in VALIDATORS_ON_SET_FIELDS:
            count_validator += 1
        if clear_msg.name in VALIDATORS_GLOBAL_ON_SET_FIELDS:
            count_validator += 1

        if count_validator > 0:
            if not is_parsed_obf_msg(obf_msg.namespace):
                return 0
            return count_validator * 250

        treated_msg_namespaces = treated_msg_namespaces.copy()
        treated_msg_namespaces.add(clear_msg.namespace)

        clear_elem_by_index = ProtoOrganization.get_flat_elements(clear_msg)
        obf_elem_by_index = ProtoOrganization.get_flat_elements(obf_msg)

        cost_matrix = np.zeros((len(clear_elem_by_index), len(obf_elem_by_index)))

        for clear_index, clear_elem in clear_elem_by_index.items():
            for obf_index, obf_elem in obf_elem_by_index.items():
                if type(clear_elem) is PField and type(obf_elem) is PField:
                    cost_matrix[clear_index][obf_index] = (
                        self.get_reliability_p_clear_field(
                            clear_msg,
                            clear_elem,
                            obf_msg,
                            obf_elem,
                            treated_msg_namespaces,
                        )
                    )
                elif type(clear_elem) is PMapField and type(obf_elem) is PMapField:
                    cost_matrix[clear_index][obf_index] = (
                        self.get_reliability_clear_map_field(
                            clear_msg,
                            clear_elem,
                            obf_msg,
                            obf_elem,
                            treated_msg_namespaces,
                        )
                    )

        row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)

        self.reliability_by_clear_namespace_with_obf_namespace[
            (clear_msg.namespace, obf_msg.namespace)
        ] = cost_matrix[row_ind, col_ind].sum() + EXTRA_RELIABILITY_MESSAGE

        return self.reliability_by_clear_namespace_with_obf_namespace[
            (clear_msg.namespace, obf_msg.namespace)
        ]

    def get_reliability_clear_map_field(
        self,
        clear_p_msg: PMessage,
        clear_map_field: PMapField,
        obf_msg: PMessage,
        obf_map_field: PMapField,
        treated_msg_namespaces: set[str],
    ) -> float:
        reliability: float = EXTRA_RELIABILITY_MAP

        reliability += RELIABILITY_BY_PROTO_BASE_FIELDS[
            clear_map_field.key_type
        ] + self.get_reliability_p_clear_field(
            clear_p_msg,
            clear_map_field.value_p_field,
            obf_msg,
            obf_map_field.value_p_field,
            treated_msg_namespaces,
        )

        return reliability

    def get_reliability_p_clear_field(
        self,
        clear_msg: PMessage,
        clear_field: PField,
        obf_msg: PMessage,
        obf_field: PField,
        treated_msg_namespaces: set[str],
    ) -> float:
        base_reliability = RELIABILITY_BY_PROTO_BASE_FIELDS.get(
            clear_field.type_name, BASE_RELIABILITY
        )

        if clear_field.cardinality == FieldCardinality.REPEATED:
            base_reliability += 1

        count_msg_values = get_count_defined_msg_field_values(
            obf_msg.namespace, obf_field.name
        )
        if count_msg_values != 0 and (
            clear_msg.name in VALIDATORS_ON_FIELD
            and clear_field.name in VALIDATORS_ON_FIELD[clear_msg.name]
        ):
            return log_reliability(count_msg_values) * (
                base_reliability + EXTRA_RELIABILITY_WITH_VALIDATOR
            )
        elif count_msg_values != 0:
            base_reliability += log_reliability(count_msg_values)

        if (
            clear_field.type_name in PROTO_BASE_FIELDS
            or obf_field.type_name in PROTO_BASE_FIELDS
        ):
            return base_reliability

        clear_sub_struct = ProtoOrganization.get_related_struct_from_type_name(
            self.clear_struct_by_namespace, clear_msg.namespace, clear_field.type_name
        )
        obf_sub_struct = ProtoOrganization.get_related_struct_from_type_name(
            self.obf_struct_by_namespace, obf_msg.namespace, obf_field.type_name
        )

        if type(clear_sub_struct) is PMessage and type(obf_sub_struct) is PMessage:
            if clear_sub_struct.namespace in treated_msg_namespaces:
                return base_reliability
            return base_reliability + self.get_reliability_clear_message(
                clear_sub_struct, obf_sub_struct, treated_msg_namespaces
            )
        elif type(clear_sub_struct) is PEnum and type(obf_sub_struct) is PEnum:
            return base_reliability + self.get_reliability_clear_enum(clear_sub_struct)

        return base_reliability
