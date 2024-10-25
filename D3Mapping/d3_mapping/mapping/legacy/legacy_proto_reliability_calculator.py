from collections import defaultdict

import numpy as np
from proto_schema_parser import FieldCardinality
from pydantic import BaseModel
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm

from d3_mapping.mapping.consts import (
    BASE_RELIABILITY,
    EXTRA_RELIABILITY_ENUM,
    EXTRA_RELIABILITY_MAP,
    EXTRA_RELIABILITY_MESSAGE,
    EXTRA_RELIABILITY_WITH_VALIDATOR,
    PROTO_BASE_FIELDS,
    RELIABILITY_BY_PROTO_BASE_FIELDS,
)
from d3_mapping.mapping.proto_organization import ProtoOrganization
from d3_mapping.mapping.validators.proto_validators import (
    VALIDATORS_ON_FIELD,
    get_count_msg_field_values,
)
from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import PField, PMapField, PMessage


class LegacyProtoReliabilityCalculator(BaseModel):
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    clear_root_namespace_by_filename: dict[str, list[str]]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_root_namespaces: list[str]
    msg_reliability_by_namespaces: dict[tuple[str, str], float] = {}
    verified_mapping_by_clear: dict[str, str]

    def get_sorted_clear_files_by_reliability(
        self,
    ) -> list[tuple[str, list[tuple[int, PMessage, float]]]]:
        sorted_clear_p_files: list[tuple[str, list[tuple[int, PMessage, float]]]] = []

        for (
            clear_filename,
            clear_namespaces,
        ) in tqdm(self.clear_root_namespace_by_filename.items()):
            comparisons: list[tuple[int, PMessage, float]] = []
            for clear_index, clear_namespace in enumerate(clear_namespaces):
                clear_struct = self.clear_struct_by_namespace[clear_namespace]
                if not isinstance(clear_struct, PMessage):
                    continue
                max_reliability_for_struct: float | None = None
                for obf_namespace in self.obf_root_namespaces:
                    obf_struct = self.obf_struct_by_namespace[obf_namespace]
                    if not isinstance(obf_struct, PMessage):
                        continue
                    reliability = self.get_reliability_clear_message(
                        clear_struct, obf_struct, set()
                    )
                    if (
                        max_reliability_for_struct is None
                        or max_reliability_for_struct < reliability
                    ):
                        max_reliability_for_struct = reliability

                if max_reliability_for_struct is not None:
                    comparisons.append(
                        (clear_index, clear_struct, max_reliability_for_struct)
                    )

            comparisons.sort(key=lambda elem: elem[2], reverse=True)
            sorted_clear_p_files.append((clear_filename, comparisons))

        sorted_clear_p_files.sort(
            key=lambda elem: max(sub_elem[2] for sub_elem in elem[1]),
            reverse=True,
        )
        return sorted_clear_p_files

    def get_reliability_by_indexes(
        self, clear_msg: PMessage, obf_msg: PMessage, treated_msg_namespaces: set[str]
    ) -> dict[int, dict[int, float]]:
        """get reliability by field  with the total reliability"""
        reliability_by_indexes: dict[int, dict[int, float]] = defaultdict(dict)

        clear_elem_by_index = ProtoOrganization.get_flat_elements(clear_msg.elements)[1]
        obf_elem_by_index = ProtoOrganization.get_flat_elements(obf_msg.elements)[1]

        for clear_index, clear_elem in clear_elem_by_index.items():
            for obf_index, obf_elem in obf_elem_by_index.items():
                if isinstance(clear_elem, PField) and isinstance(obf_elem, PField):
                    reliability_by_indexes[clear_index][obf_index] = (
                        self.get_reliability_p_clear_field(
                            clear_msg,
                            clear_elem,
                            obf_msg,
                            obf_elem,
                            treated_msg_namespaces,
                        )
                    )
                elif isinstance(clear_elem, PMapField) and isinstance(
                    obf_elem, PMapField
                ):
                    reliability_by_indexes[clear_index][obf_index] = (
                        self.get_reliability_clear_map_field(
                            clear_msg,
                            clear_elem,
                            obf_msg,
                            obf_elem,
                            treated_msg_namespaces,
                        )
                    )
                else:
                    reliability_by_indexes[clear_index][obf_index] = BASE_RELIABILITY

        # if clear_msg.name == "StatedElement" and obf_msg.name == "jub":
        #     print(reliability_by_indexes)

        return reliability_by_indexes

    def get_reliability_clear_enum(self, enum: PEnum) -> float:
        return len(enum.elements) + EXTRA_RELIABILITY_ENUM

    def get_reliability_clear_message(
        self, clear_msg: PMessage, obf_msg: PMessage, treated_msg_namespaces: set[str]
    ) -> float:
        if (
            clear_msg.namespace,
            obf_msg.namespace,
        ) in self.msg_reliability_by_namespaces:
            return self.msg_reliability_by_namespaces[
                (clear_msg.namespace, obf_msg.namespace)
            ]

        if (
            clear_msg.name in self.verified_mapping_by_clear
            and self.verified_mapping_by_clear[clear_msg.name] == obf_msg.name
        ):
            return 999

        treated_msg_namespaces = treated_msg_namespaces.copy()
        treated_msg_namespaces.add(clear_msg.namespace)

        len_clear_elems, clear_elem_by_index = ProtoOrganization.get_flat_elements(
            clear_msg.elements
        )
        len_obf_elems, obf_elem_by_index = ProtoOrganization.get_flat_elements(
            obf_msg.elements
        )

        cost_matrix = np.zeros((len_clear_elems, len_obf_elems))

        for clear_index, clear_elem in clear_elem_by_index.items():
            for obf_index, obf_elem in obf_elem_by_index.items():
                if isinstance(clear_elem, PField) and isinstance(obf_elem, PField):
                    cost_matrix[clear_index][obf_index] = (
                        self.get_reliability_p_clear_field(
                            clear_msg,
                            clear_elem,
                            obf_msg,
                            obf_elem,
                            treated_msg_namespaces,
                        )
                    )
                elif isinstance(clear_elem, PMapField) and isinstance(
                    obf_elem, PMapField
                ):
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

        self.msg_reliability_by_namespaces[(clear_msg.namespace, obf_msg.namespace)] = (
            cost_matrix[row_ind, col_ind].sum() + EXTRA_RELIABILITY_MESSAGE
        )

        return self.msg_reliability_by_namespaces[
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

        count_msg_values = get_count_msg_field_values(obf_msg.namespace, obf_field.name)
        if count_msg_values != 0 and (
            clear_msg.name in VALIDATORS_ON_FIELD
            and clear_field.name in VALIDATORS_ON_FIELD[clear_msg.name]
        ):
            return count_msg_values * (
                base_reliability + EXTRA_RELIABILITY_WITH_VALIDATOR
            )

        if (
            clear_field.type_name in PROTO_BASE_FIELDS
            or obf_field.type_name in PROTO_BASE_FIELDS
        ):
            return base_reliability

        clear_sub_struct = ProtoOrganization.get_related_struct(
            self.clear_struct_by_namespace, clear_msg.namespace, clear_field.type_name
        )
        obf_sub_struct = ProtoOrganization.get_related_struct(
            self.obf_struct_by_namespace, obf_msg.namespace, obf_field.type_name
        )

        if isinstance(clear_sub_struct, PMessage) and isinstance(
            obf_sub_struct, PMessage
        ):
            if clear_sub_struct.namespace in treated_msg_namespaces:
                return base_reliability
            return base_reliability + self.get_reliability_clear_message(
                clear_sub_struct, obf_sub_struct, treated_msg_namespaces
            )
        elif isinstance(clear_sub_struct, PEnum) and isinstance(obf_sub_struct, PEnum):
            return base_reliability + self.get_reliability_clear_enum(clear_sub_struct)

        return base_reliability
