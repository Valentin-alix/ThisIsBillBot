from dataclasses import dataclass, field
from typing import cast

import numpy as np
from proto_schema_parser import FieldCardinality
import pulp
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm


from d3_mapping.controller.instancied_msg_info_controller import MSG_INFO_BY_NAME
from d3_mapping.mapping.consts import PROTO_BASE_FIELDS
from d3_mapping.mapping.proto_organization import ProtoOrganization
from d3_mapping.mapping.proto_reliability_calculator import ProtoReliabilityCalculator
from d3_mapping.mapping.validators.proto_validators import (
    VALIDATORS_ON_FIELD,
    VALIDATORS_ON_SET_FIELDS,
    is_condition_respected,
)
from d3_mapping.models.mapping_info import FieldMapping, MappingInfo
from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import (
    PField,
    PMapField,
    PMessage,
)
from d3_mapping.utils import Percentage, set_percentage


@dataclass
class ProtoMapper:
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    clear_root_namespaces: list[str]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_root_namespaces: list[str]
    reliability_calculator: ProtoReliabilityCalculator

    verified_msg_by_obf: dict[str, str]
    verified_mapping_field_by_clear: dict[str, dict[str, str]]

    msg_mapping_info_by_obf_name: dict[str, MappingInfo] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self):
        self.verified_msg_by_clear = {
            value: key for key, value in self.verified_msg_by_obf.items()
        }

    def run_mapping(self) -> dict[str, MappingInfo]:
        for obf_namespace in tqdm(self.obf_root_namespaces):
            related_clear_msg_name = self.verified_msg_by_obf.get(obf_namespace)
            if related_clear_msg_name is None:
                # print(f"No Mapping for {obf_namespace}")
                continue
            related_clear_namespace = next(
                (
                    namespace
                    for namespace in self.clear_struct_by_namespace
                    if namespace.split(".")[-1] == related_clear_msg_name
                ),
                None,
            )
            if related_clear_namespace is None:
                # print(f"New message : {related_clear_msg_name} from {obf_namespace}")
                continue
            self.get_comparison_message(related_clear_namespace, obf_namespace, set())

            related_clear_msg = self.clear_struct_by_namespace[related_clear_namespace]
            assert isinstance(related_clear_msg, PMessage)

            related_obf_msg = self.obf_struct_by_namespace[obf_namespace]
            assert isinstance(related_obf_msg, PMessage)

            self.add_new_msg_mapping(related_clear_msg, related_obf_msg, set())

        clear_msg_namespace_treateds = {
            mapping_info.clear_msg_name
            for mapping_info in self.msg_mapping_info_by_obf_name.values()
        }
        remaining_clear_msgs = [
            msg
            for namespace in self.clear_root_namespaces
            if namespace not in clear_msg_namespace_treateds
            and isinstance((msg := self.clear_struct_by_namespace[namespace]), PMessage)
            and msg.name in ["GameMessage"]
        ]
        # print(
        #     f"Remaining clear msgs : {[msg.namespace for msg in remaining_clear_msgs]}"
        # )
        for clear_msg in tqdm(remaining_clear_msgs):
            sim_obf_msg = self.get_most_similar_obf_msg(clear_msg)
            if sim_obf_msg is None:
                continue
            sim, obf_namespace = sim_obf_msg
            if sim < 0.75:
                continue
            related_obf_struct = self.obf_struct_by_namespace[obf_namespace]
            assert isinstance(related_obf_struct, PMessage)
            self.add_new_msg_mapping(clear_msg, related_obf_struct, set())

        return self.msg_mapping_info_by_obf_name

    def get_most_similar_obf_msg(self, clear_msg: PMessage):
        most_sim_msg: tuple[Percentage, str] | None = None
        for obf_namespace in self.obf_root_namespaces:
            related_obf_struct = self.obf_struct_by_namespace[obf_namespace]
            if not isinstance(related_obf_struct, PMessage):
                continue
            sim, _ = self.get_comparison_message(
                clear_msg.namespace, obf_namespace, set()
            )
            if most_sim_msg is None or most_sim_msg[0] < sim:
                most_sim_msg = (sim, obf_namespace)

        return most_sim_msg

    def add_new_msg_mapping(
        self, clear_msg: PMessage, obf_msg: PMessage, treated_namespace: set[str]
    ):
        if obf_msg.namespace in self.msg_mapping_info_by_obf_name:
            return

        sim, field_mapping = self.get_comparison_message(
            clear_msg.namespace, obf_msg.namespace, treated_namespace
        )

        self.msg_mapping_info_by_obf_name[obf_msg.namespace] = MappingInfo(
            clear_msg_name=clear_msg.namespace,
            similarity=sim,
            field_mapping=field_mapping,
        )

        treated_namespace = treated_namespace.copy()
        treated_namespace.add(clear_msg.namespace)

        # here we also add on mapping sub namespaces
        clear_flat_elements = ProtoOrganization.get_flat_elements(
            clear_msg.elements
        ).values()
        for obf_elem in ProtoOrganization.get_flat_elements(obf_msg.elements).values():
            obf_type_name = (
                obf_elem.value_p_field.type_name
                if isinstance(obf_elem, PMapField)
                else obf_elem.type_name
            )
            if obf_type_name in PROTO_BASE_FIELDS:
                continue

            if obf_elem.name not in field_mapping:
                continue
            related_clear_field_name = field_mapping[obf_elem.name][0]
            if related_clear_field_name is None:
                continue
            related_clear_elem = next(
                elem
                for elem in clear_flat_elements
                if elem.name == related_clear_field_name
            )
            clear_type_name = (
                related_clear_elem.value_p_field.type_name
                if isinstance(related_clear_elem, PMapField)
                else related_clear_elem.type_name
            )
            if clear_type_name in PROTO_BASE_FIELDS:
                continue

            sub_obf_nested_namespace = f"{obf_msg.namespace}.{obf_type_name}"
            sub_obf_namespace = (
                sub_obf_nested_namespace
                if sub_obf_nested_namespace in self.obf_struct_by_namespace
                else obf_type_name
            )
            if sub_obf_namespace in treated_namespace:
                continue

            sub_clear_nested_namespace = f"{clear_msg.namespace}.{clear_type_name}"
            sub_clear_namespace = (
                sub_clear_nested_namespace
                if sub_clear_nested_namespace in self.clear_struct_by_namespace
                else clear_type_name
            )

            sub_clear_struct = self.clear_struct_by_namespace[sub_clear_namespace]
            sub_obf_struct = self.obf_struct_by_namespace[sub_obf_namespace]

            if isinstance(sub_clear_struct, PMessage) and isinstance(
                sub_obf_struct, PMessage
            ):
                self.add_new_msg_mapping(
                    sub_clear_struct, sub_obf_struct, treated_namespace
                )

    def get_comparison_message(
        self,
        clear_namespace: str,
        obf_namespace: str,
        treated_msg_namespaces: set[str],
    ) -> tuple[Percentage, FieldMapping]:
        def proxy_comparison_msg(
            sim: Percentage, sim_by_fields: dict[str, tuple[str | None, Percentage]]
        ):
            """wrapper around return values"""
            if clear_msg.name in self.verified_msg_by_clear:
                sim = (
                    0
                    if obf_msg.name != self.verified_msg_by_clear[clear_msg.name]
                    else 1
                )
            if obf_msg.name in self.verified_msg_by_obf:
                sim = (
                    0 if clear_msg.name != self.verified_msg_by_obf[obf_msg.name] else 1
                )

            return set_percentage(sim), sim_by_fields

        clear_msg = self.clear_struct_by_namespace[clear_namespace]
        assert isinstance(clear_msg, PMessage)

        obf_msg = self.obf_struct_by_namespace[obf_namespace]
        assert isinstance(obf_msg, PMessage)

        if (
            clear_msg.name in self.verified_msg_by_clear
            and obf_msg.name != self.verified_msg_by_clear[clear_msg.name]
        ):
            return proxy_comparison_msg(0, {})
        if (
            obf_msg.name in self.verified_msg_by_obf
            and clear_msg.name != self.verified_msg_by_obf[obf_msg.name]
        ):
            return proxy_comparison_msg(0, {})

        if len(clear_msg.elements) == 0:
            if len(obf_msg.elements) == 0:
                return proxy_comparison_msg(1, {})
            return proxy_comparison_msg(0, {})
        if len(obf_msg.elements) == 0:
            return proxy_comparison_msg(0, {})

        treated_msg_namespaces = treated_msg_namespaces.copy()
        treated_msg_namespaces.add(clear_msg.namespace)

        reliability_by_indexes = self.reliability_calculator.get_reliability_by_indexes(
            clear_msg, obf_msg, treated_msg_namespaces
        )
        clear_elem_by_index = ProtoOrganization.get_flat_elements(clear_msg.elements)
        obf_elem_by_index = ProtoOrganization.get_flat_elements(obf_msg.elements)

        cost_matrix, sim_by_indexes = self.get_matrix_cost_between_field(
            clear_elem_by_index,
            clear_msg,
            obf_elem_by_index,
            obf_msg,
            reliability_by_indexes,
            treated_msg_namespaces,
        )

        if clear_msg.name in VALIDATORS_ON_SET_FIELDS:
            solver = pulp.PULP_CBC_CMD(msg=False, presolve=True)
            model = pulp.LpProblem("Assignment", pulp.LpMaximize)
            row, col = cost_matrix.shape

            x = [
                [pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(col)]
                for i in range(row)
            ]
            # Fonction objectif : somme des coûts choisis
            model += pulp.lpSum(
                x[i][j] * cost_matrix[i][j] for i in range(row) for j in range(col)
            )
            # Contraintes : chaque ligne assignée à une seule colonne
            for i in range(row):
                model += pulp.lpSum(x[i][j] for j in range(col)) <= 1
            # Chaque colonne ne peut être assignée qu'une fois
            for j in range(col):
                model += pulp.lpSum(x[i][j] for i in range(row)) <= 1

            while True:
                model.solve(solver)

                sim_by_fields: dict[str, tuple[str | None, Percentage]] = {}
                solution: list[tuple[int, int]] = []
                total_reliability: float = 0
                for i in range(row):
                    for j in range(col):
                        if not pulp.value(x[i][j]) == 1:
                            continue
                        solution.append((i, j))
                        clear_field_name, obf_field_name, field_sim = sim_by_indexes[
                            (i, j)
                        ]
                        sim_by_fields[obf_field_name] = (clear_field_name, field_sim)
                        total_reliability += reliability_by_indexes[i][j]

                is_valid = self.is_valid_sim_by_fields(
                    clear_msg.name, obf_msg.name, sim_by_fields
                )
                if not is_valid:
                    model += (
                        pulp.lpSum(x[i][j] for (i, j) in solution) <= len(solution) - 1
                    )
                else:
                    break
            total_sim = cast(float, pulp.value(model.objective) or 0)
        else:
            row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)
            sim_by_fields: dict[str, tuple[str | None, Percentage]] = {}
            total_reliability: float = 0
            for i, j in zip(row_ind, col_ind):
                clear_field_name, obf_field_name, field_sim = sim_by_indexes[(i, j)]
                sim_by_fields[obf_field_name] = (clear_field_name, field_sim)
                total_reliability += reliability_by_indexes[i][j]
            total_sim = cost_matrix[row_ind, col_ind].sum()

        for obf_elem in obf_elem_by_index.values():
            # fill empty obf field mapping
            if obf_elem.name not in sim_by_fields:
                sim_by_fields[obf_elem.name] = (None, 0)

        if total_reliability == 0:
            return proxy_comparison_msg(0, {})

        msg_sim = total_sim / total_reliability
        msg_sim = self.get_value_with_len_malus(
            msg_sim, len(clear_elem_by_index), len(obf_elem_by_index)
        )

        return proxy_comparison_msg(msg_sim, sim_by_fields)

    def is_valid_sim_by_fields(
        self,
        clear_msg_name: str,
        obf_msg_name: str,
        sim_by_fields: dict[str, tuple[str | None, Percentage]],
    ):
        validator_on_whole_msg = VALIDATORS_ON_SET_FIELDS.get(clear_msg_name)
        if validator_on_whole_msg and (
            parsed_obf_msg_infos := MSG_INFO_BY_NAME.get(obf_msg_name)
        ):
            for obf_msg_info in parsed_obf_msg_infos.obf_msg_info:
                value_by_field_mapped_to_clear = {
                    mapped_field_name: value
                    for key, value in obf_msg_info.value_by_field_array.items()
                    if (mapped_field_name := sim_by_fields[key][0]) is not None
                }
                if not validator_on_whole_msg(value_by_field_mapped_to_clear):
                    return False
        return True

    def get_matrix_cost_between_field(
        self,
        clear_elem_by_index: dict[int, PField | PMapField],
        clear_msg: PMessage,
        obf_elem_by_index: dict[int, PField | PMapField],
        obf_msg: PMessage,
        reliability_by_indexes: dict[int, dict[int, float]],
        treated_msg_namespaces: set[str],
    ) -> tuple[
        np.ndarray[tuple[int, int], np.dtype[np.float64]],
        dict[tuple[int, int], tuple[str, str, Percentage]],
    ]:
        """get matrix cost between each field, indexes of result need to be correlated"""
        cost_matrix = np.zeros((len(clear_elem_by_index), len(obf_elem_by_index)))
        sim_by_numbers: dict[tuple[int, int], tuple[str, str, Percentage]] = {}

        for clear_index, clear_msg_elem in clear_elem_by_index.items():
            for obf_index, obf_msg_elem in obf_elem_by_index.items():
                if isinstance(clear_msg_elem, PField) and isinstance(
                    obf_msg_elem, PField
                ):
                    cost_elem = self.compare_p_field(
                        clear_msg,
                        clear_msg_elem,
                        obf_msg,
                        obf_msg_elem,
                        treated_msg_namespaces,
                    )
                elif isinstance(clear_msg_elem, PMapField) and isinstance(
                    obf_msg_elem, PMapField
                ):
                    cost_elem = self.compare_map_fields(
                        clear_msg,
                        clear_msg_elem,
                        obf_msg,
                        obf_msg_elem,
                        treated_msg_namespaces,
                    )
                else:
                    cost_elem = 0

                # print(f"{clear_msg_elem.name} : {obf_msg_elem.name} with {cost_elem}")
                sim_by_numbers[(clear_index, obf_index)] = (
                    clear_msg_elem.name,
                    obf_msg_elem.name,
                    cost_elem,
                )
                cost_matrix[clear_index, obf_index] = (
                    cost_elem * reliability_by_indexes[clear_index][obf_index]
                )

        return cost_matrix, sim_by_numbers

    def compare_map_fields(
        self,
        clear_msg: PMessage,
        clear_p_map_field: PMapField,
        obf_msg: PMessage,
        obf_p_map_field: PMapField,
        treated_msg_namespace: set[str],
    ) -> float:
        if clear_p_map_field.key_type != obf_p_map_field.key_type:
            return 0

        return set_percentage(
            self.compare_p_field(
                clear_msg,
                clear_p_map_field.value_p_field,
                obf_msg,
                obf_p_map_field.value_p_field,
                treated_msg_namespace,
            )
        )

    def compare_p_field(
        self,
        clear_msg: PMessage,
        clear_p_field: PField,
        obf_msg: PMessage,
        obf_p_field: PField,
        treated_msg_namespace: set[str],
    ) -> float:
        if (
            clear_msg.name in self.verified_mapping_field_by_clear
            and clear_p_field.name
            in self.verified_mapping_field_by_clear[clear_msg.name]
        ):
            if (
                self.verified_mapping_field_by_clear[clear_msg.name][clear_p_field.name]
                == obf_p_field.name
            ):
                return 1
            return 0

        if (clear_p_field.cardinality is FieldCardinality.REPEATED) != (
            obf_p_field.cardinality is FieldCardinality.REPEATED
        ):
            return 0

        if (
            clear_p_field.type_name in PROTO_BASE_FIELDS
            or obf_p_field.type_name in PROTO_BASE_FIELDS
        ) and clear_p_field.type_name != obf_p_field.type_name:
            return 0

        related_validator = VALIDATORS_ON_FIELD.get(clear_msg.name)
        if related_validator:
            related_field_validators = related_validator.get(clear_p_field.name)
            if related_field_validators:
                is_respected, value = is_condition_respected(
                    obf_msg.namespace, obf_p_field.name, related_field_validators
                )
                # if obf_p_field.name == "edcu" and clear_p_field.name == "npc_id":
                #     print(
                #         f"Condition {is_respected} respected for value {value} {obf_msg.namespace} {related_field_validators}"
                #     )
                if not is_respected:
                    return 0

        if clear_p_field.type_name in PROTO_BASE_FIELDS:
            assert (
                obf_p_field.type_name in PROTO_BASE_FIELDS
                and clear_p_field.type_name == obf_p_field.type_name
            )
            return 1

        clear_struct = ProtoOrganization.get_related_struct(
            self.clear_struct_by_namespace, clear_msg.namespace, clear_p_field.type_name
        )
        obf_struct = ProtoOrganization.get_related_struct(
            self.obf_struct_by_namespace, obf_msg.namespace, obf_p_field.type_name
        )
        if isinstance(clear_struct, PMessage) and isinstance(obf_struct, PMessage):
            if clear_struct.namespace in treated_msg_namespace:
                return 1
            related_validator = VALIDATORS_ON_FIELD.get(clear_msg.name)
            if related_validator:
                related_field_validators = related_validator.get(clear_p_field.name)
                if related_field_validators and not is_condition_respected(
                    obf_msg.namespace, obf_p_field.name, related_field_validators
                ):
                    return 0
            return set_percentage(
                self.get_comparison_message(
                    clear_struct.namespace, obf_struct.namespace, treated_msg_namespace
                )[0]
            )
        elif isinstance(clear_struct, PEnum) and isinstance(obf_struct, PEnum):
            return set_percentage(self.get_sim_enum(clear_struct, obf_struct))

        return 0

    def get_sim_enum(self, clear_enum: PEnum, obf_enum: PEnum) -> float:
        return self.get_value_with_len_malus(
            1, len(clear_enum.elements), len(obf_enum.elements)
        )

    def get_value_with_len_malus(
        self, value: float, len_clear_elems: int, len_obf_elems: int
    ) -> float:
        malus = 2 if len_clear_elems > len_obf_elems else 1
        if len_obf_elems - 1 == len_clear_elems:
            return value / 1.1

        min_len_elems = min(len_clear_elems, len_obf_elems)
        max_len_elems = max(len_clear_elems, len_obf_elems)
        return value * (min_len_elems / max_len_elems) / malus
