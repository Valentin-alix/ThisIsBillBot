import math
from dataclasses import dataclass, field
from functools import wraps
from typing import cast

from cachetools import cached
import numpy as np
import pulp
from proto_schema_parser import FieldCardinality
from scipy.optimize import linear_sum_assignment

from d3_mapping.consts import PROTO_BASE_FIELDS, EntryMsg
from d3_mapping.mapping.malus_utils import get_value_with_len_malus
from d3_mapping.mapping.proto_organization import ProtoOrganization
from d3_mapping.mapping.proto_reliability_calculator import ProtoReliabilityCalculator
from d3_mapping.mapping.validators.proto_field_validators import (
    VALIDATORS_GLOBAL_ON_SET_FIELDS,
    VALIDATORS_ON_FIELD,
    VALIDATORS_ON_SET_FIELDS,
    is_condition_respected,
)
from d3_mapping.mapping.validators.proto_validator import ProtoValidator
from d3_mapping.models.mapping_info import FieldMapping, MappingInfo
from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import (
    PField,
    PMapField,
    PMessage,
)
from d3_mapping.utils import Percentage, set_percentage

type PulpMappingStruct = dict[tuple[tuple[str, ...], tuple[str, ...]], float]


def compare_p_enum(clear_enum: PEnum, obf_enum: PEnum) -> float:
    return set_percentage(
        get_value_with_len_malus(1, len(clear_enum.elements), len(obf_enum.elements))
    )


def enforce_proxy_compare_field(compare_field_func):
    @wraps(compare_field_func)
    def wrapper(
        self: "ComparisonEngine",
        clear_msg: PMessage,
        clear_p_field: PField,
        obf_msg: PMessage,
        obf_p_field: PField,
        treated_clear_namespaces: set[str],
    ) -> tuple[Percentage, MappingInfo | None]:
        sim, mapping_info = compare_field_func(
            self,
            clear_msg,
            clear_p_field,
            obf_msg,
            obf_p_field,
            treated_clear_namespaces,
        )
        if (
            clear_msg.name in self.verified_mapping_field_by_clear
            and clear_p_field.name
            in self.verified_mapping_field_by_clear[clear_msg.name]
        ):
            if (
                self.verified_mapping_field_by_clear[clear_msg.name][clear_p_field.name]
                == obf_p_field.name
            ):
                sim = 1
            else:
                sim = 0
        return sim, mapping_info

    return wrapper


def enforce_proxy_compare_msg(compare_msg_func):
    @wraps(compare_msg_func)
    def wrapper(
        self: "ComparisonEngine",
        clear_msg: PMessage,
        obf_msg: PMessage,
        treated_clear_namespaces: set[str],
    ) -> MappingInfo:
        if obf_msg.namespace in self._added_mapping_by_obf_namespaces:
            obf_mapping_info = self._added_mapping_by_obf_namespaces[obf_msg.namespace]
            if obf_mapping_info.clear_msg_namespace == clear_msg.namespace:
                return obf_mapping_info
            else:
                return MappingInfo(
                    similarity=0,
                    clear_msg_namespace=clear_msg.namespace,
                    field_mapping={},
                )

        is_an_entry_msg = any(
            clear_msg.namespace.endswith(entry_msg) for entry_msg in EntryMsg
        )

        mapping_info: MappingInfo
        if (
            is_an_entry_msg
            and clear_msg.name in self.verified_msg_by_clear
            and obf_msg.name != self.verified_msg_by_clear[clear_msg.name]
        ):
            mapping_info = MappingInfo(
                similarity=0, clear_msg_namespace=clear_msg.namespace, field_mapping={}
            )
        elif (
            obf_msg.name in self.verified_msg_by_obf
            and clear_msg.name != self.verified_msg_by_obf[obf_msg.name]
        ):
            mapping_info = MappingInfo(
                similarity=0, clear_msg_namespace=clear_msg.namespace, field_mapping={}
            )
        elif len(clear_msg.elements) == 0 and len(obf_msg.elements) == 0:
            mapping_info = MappingInfo(
                similarity=1, clear_msg_namespace=clear_msg.namespace, field_mapping={}
            )
        elif (len(clear_msg.elements) == 0) != (len(obf_msg.elements) == 0):
            mapping_info = MappingInfo(
                similarity=0, clear_msg_namespace=clear_msg.namespace, field_mapping={}
            )
        else:
            mapping_info: MappingInfo = compare_msg_func(
                self, clear_msg, obf_msg, treated_clear_namespaces
            )
            if is_an_entry_msg and clear_msg.name in self.verified_msg_by_clear:
                mapping_info.similarity = (
                    0
                    if obf_msg.name != self.verified_msg_by_clear[clear_msg.name]
                    else 1
                )
            if obf_msg.name in self.verified_msg_by_obf:
                mapping_info.similarity = (
                    0 if clear_msg.name != self.verified_msg_by_obf[obf_msg.name] else 1
                )

        mapping_info.similarity = set_percentage(mapping_info.similarity)
        return mapping_info

    return wrapper


@dataclass
class ComparisonEngine:
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    reliability_calculator: ProtoReliabilityCalculator
    proto_validator: ProtoValidator

    verified_msg_by_obf: dict[str, str]
    verified_mapping_field_by_clear: dict[str, dict[str, str]]

    _added_mapping_by_obf_namespaces: dict[str, MappingInfo] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self):
        self.verified_msg_by_clear = {
            value: key for key, value in self.verified_msg_by_obf.items()
        }

    @enforce_proxy_compare_msg
    def get_comparison_message(
        self,
        clear_msg: PMessage,
        obf_msg: PMessage,
        treated_clear_namespaces: set[str],
    ) -> MappingInfo:
        treated_clear_namespaces = treated_clear_namespaces.copy()
        treated_clear_namespaces.add(clear_msg.namespace)

        len_clear_elems = len(ProtoOrganization.get_flat_elements(clear_msg))
        len_obf_elems = len(ProtoOrganization.get_flat_elements(obf_msg))

        if (
            clear_msg.name in VALIDATORS_ON_SET_FIELDS
            or clear_msg.name in VALIDATORS_GLOBAL_ON_SET_FIELDS
        ):
            total_sim, total_reliability, clear_by_obf_field_mapping = (
                self.get_deep_best_field_mapping_combination(
                    clear_msg, obf_msg, treated_clear_namespaces
                )
            )
        else:
            clear_elem_by_index = ProtoOrganization.get_flat_elements(clear_msg)
            obf_elem_by_index = ProtoOrganization.get_flat_elements(obf_msg)

            total_sim, total_reliability, clear_by_obf_field_mapping = (
                self.get_flat_best_field_mapping_combination(
                    clear_msg,
                    obf_msg,
                    clear_elem_by_index,
                    obf_elem_by_index,
                    treated_clear_namespaces,
                )
            )

        if total_reliability == 0:
            return MappingInfo(
                clear_msg_namespace=clear_msg.namespace, similarity=0, field_mapping={}
            )

        msg_sim = total_sim / total_reliability
        msg_sim = get_value_with_len_malus(msg_sim, len_clear_elems, len_obf_elems)

        return MappingInfo(
            clear_msg_namespace=clear_msg.namespace,
            similarity=msg_sim,
            field_mapping=clear_by_obf_field_mapping,
        )

    def get_flat_best_field_mapping_combination(
        self,
        clear_msg: PMessage,
        obf_msg: PMessage,
        clear_elem_by_index: dict[int, PMapField | PField],
        obf_elem_by_index: dict[int, PMapField | PField],
        treated_clear_namespaces: set[str],
    ):
        clear_by_obf_field_mapping: FieldMapping = {}

        reliability_by_indexes = (
            self.reliability_calculator.get_flat_reliability_by_indexes(
                clear_msg, obf_msg, treated_clear_namespaces
            )
        )

        cost_matrix, mapping_by_indexes = self.get_matrix_cost_between_field(
            clear_msg,
            clear_elem_by_index,
            obf_msg,
            obf_elem_by_index,
            reliability_by_indexes,
            treated_clear_namespaces,
        )

        row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)

        total_reliability: float = 0

        for i, j in zip(row_ind, col_ind):
            obf_field_name, clear_mapping_info = mapping_by_indexes[(i, j)]
            clear_by_obf_field_mapping[obf_field_name] = clear_mapping_info
            total_reliability += 1 + math.log(reliability_by_indexes[i][j], 2)

        total_sim = cost_matrix[row_ind, col_ind].sum()

        for obf_elem in obf_elem_by_index.values():
            # fill empty obf field mapping
            if obf_elem.name not in clear_by_obf_field_mapping:
                clear_by_obf_field_mapping[obf_elem.name] = None

        return total_sim, total_reliability, clear_by_obf_field_mapping

    @cached(
        cache={},
        key=lambda _, clear_msg, obf_msg, __: (clear_msg.namespace, obf_msg.namespace),
    )
    def get_deep_best_field_mapping_combination(
        self, clear_msg: PMessage, obf_msg: PMessage, treated_clear_namespaces: set[str]
    ):
        # Actuellement il faut faire gaffe si on a un big message il va pas utiliser la validation sur les sub messages
        # print(f"solving msg {clear_msg.name} with obf msg {obf_msg.name}")

        solver = pulp.PULP_CBC_CMD(msg=False, presolve=True)
        total_reliability: float = 0

        sim_by_mapping, reliability_by_mapping = (
            self.get_deep_sim_with_reliability_by_pair(
                None, clear_msg, None, obf_msg, treated_clear_namespaces
            )
        )

        model = pulp.LpProblem("BestPathMapping", pulp.LpMaximize)

        # Variables binaires : 1 si on sélectionne cette correspondance, 0 sinon
        lp_variable_by_path = {
            (clear_path, obf_path): pulp.LpVariable(
                f"map_{'_'.join(clear_path)}__{'_'.join(obf_path)}", cat="Binary"
            )
            for (clear_path, obf_path) in sim_by_mapping
        }

        for (clear_path, obf_path), var in lp_variable_by_path.items():
            for i in range(1, len(clear_path)):
                clear_parent = clear_path[:i]
                obf_parent = obf_path[:i]
                parent_var = lp_variable_by_path[(clear_parent, obf_parent)]
                model += (
                    var <= parent_var,
                    f"parent_constraint_{var.name}_le_{parent_var.name}",
                )

        # Objectif : maximiser la somme des similarités sélectionnées
        model += pulp.lpSum(
            sim_by_mapping[(clear_path, obf_path)]
            * lp_variable_by_path[(clear_path, obf_path)]
            for (clear_path, obf_path) in sim_by_mapping
        )

        # Contrainte : une seule correspondance par chemin de gauche (clé "clair")
        pairs_by_path: dict[tuple[str, ...], list] = {}
        for clear_path, obf_path in sim_by_mapping:
            pairs_by_path.setdefault(clear_path, []).append((clear_path, obf_path))
            pairs_by_path.setdefault(obf_path, []).append((clear_path, obf_path))

        for pairs in pairs_by_path.values():
            model += pulp.lpSum(lp_variable_by_path[pair] for pair in pairs) <= 1

        max_iteration = 100
        while True:
            max_iteration -= 1
            if max_iteration < 0:
                raise ValueError(
                    f"too much iteration on pulp solution on comparing {clear_msg.name} with {obf_msg.name}"
                )
            model.solve(solver)

            total_reliability = 0
            mapping_result: dict[tuple[tuple[str, ...], tuple[str, ...]], float] = {}
            for clear_path, obf_path in sim_by_mapping:
                if pulp.value(lp_variable_by_path[(clear_path, obf_path)]) != 1:
                    continue
                mapping_result[(clear_path, obf_path)] = (
                    sim_by_mapping[(clear_path, obf_path)]
                    / reliability_by_mapping[(clear_path, obf_path)]
                )
                total_reliability += reliability_by_mapping[(clear_path, obf_path)]

            clear_by_obf_field_mapping = self.convert_pulp_result_to_field_mapping(
                clear_msg, obf_msg, mapping_result
            )
            is_valid = self.proto_validator.is_valid_clear_by_obf_field_mapping(
                treated_clear_namespaces,
                clear_msg,
                obf_msg,
                clear_by_obf_field_mapping,
            )
            if not is_valid:
                model += (
                    pulp.lpSum(lp_variable_by_path[pair] for pair in mapping_result)
                    <= len(mapping_result) - 1
                )
                # print("invalid search for an other combination...")
            else:
                break
        total_sim = cast(float, pulp.value(model.objective) or 0)

        return total_sim, total_reliability, clear_by_obf_field_mapping

    def get_deep_sim_with_reliability_by_pair(
        self,
        clear_prefix: tuple[str, ...] | None,
        clear_msg: PMessage,
        obf_prefix: tuple[str, ...] | None,
        obf_msg: PMessage,
        treated_clear_namespaces: set[str],
    ):
        sim_by_mapping: PulpMappingStruct = {}
        reliability_by_mapping: dict[
            tuple[tuple[str, ...], tuple[str, ...]], float
        ] = {}

        for clear_elem in ProtoOrganization.get_flat_elements(clear_msg).values():
            for obf_elem in ProtoOrganization.get_flat_elements(obf_msg).values():
                if type(clear_elem) is PField and type(obf_elem) is PField:
                    cost, mapping_info = self.compare_p_field(
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
                    cost, mapping_info = self.compare_map_fields(
                        clear_msg,
                        clear_elem,
                        obf_msg,
                        obf_elem,
                        treated_clear_namespaces,
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
                reliability_by_mapping[mapping_key] = math.log(1 + reliability_field, 2)
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
                    sub_sim_by_mapping, sub_reliability_by_mapping = (
                        self.get_deep_sim_with_reliability_by_pair(
                            clear_prefix + (clear_elem.name,)
                            if clear_prefix is not None
                            else (clear_elem.name,),
                            sub_clear_struct,
                            obf_prefix + (obf_elem.name,)
                            if obf_prefix is not None
                            else (obf_elem.name,),
                            sub_obf_struct,
                            treated_clear_namespaces | {sub_clear_struct.namespace},
                        )
                    )
                    sim_by_mapping |= sub_sim_by_mapping
                    reliability_by_mapping |= sub_reliability_by_mapping

        return sim_by_mapping, reliability_by_mapping

    def convert_pulp_result_to_field_mapping(
        self, clear_msg: PMessage, obf_msg: PMessage, pulp_result: PulpMappingStruct
    ) -> FieldMapping:
        clear_by_obf_field_mapping: FieldMapping = {}
        sorted_pulp_result = sorted(
            pulp_result.items(), key=lambda elem: len(elem[0][0])
        )

        while len(sorted_pulp_result) != 0:
            pair, sim = sorted_pulp_result[0]
            clear_path, obf_path = pair
            prefix_clear_path = clear_path[0]
            prefix_obf_path = obf_path[0]

            if len(clear_path) == 1:
                assert len(obf_path) == 1
                if (
                    sub_struct := ProtoOrganization.get_related_struct_from_field_name(
                        self.clear_struct_by_namespace, clear_msg, prefix_clear_path
                    )
                ) is not None and type(sub_struct) is PMessage:
                    mapping_info = MappingInfo(
                        clear_msg_namespace=sub_struct.namespace,
                        similarity=sim,
                        field_mapping={},
                    )
                else:
                    mapping_info = None

                clear_by_obf_field_mapping[prefix_obf_path] = (
                    sim,
                    prefix_clear_path,
                    mapping_info,
                )
                sorted_pulp_result.pop(0)
                continue

            assert prefix_obf_path in clear_by_obf_field_mapping
            sub_clear_msg = ProtoOrganization.get_related_struct_from_field_name(
                self.clear_struct_by_namespace, clear_msg, prefix_clear_path
            )
            assert type(sub_clear_msg) is PMessage
            sub_obf_msg = ProtoOrganization.get_related_struct_from_field_name(
                self.obf_struct_by_namespace, obf_msg, prefix_obf_path
            )
            assert type(sub_obf_msg) is PMessage

            _related_field_mapping = clear_by_obf_field_mapping[prefix_obf_path]
            assert _related_field_mapping is not None
            assert (mapping_info := _related_field_mapping[2]) is not None

            # here we first prefix
            _related_sub_pulp_result: PulpMappingStruct = {}
            for (clear_path, obf_path), value in pulp_result.items():
                if clear_path[0] == prefix_clear_path and len(clear_path) > 1:
                    sorted_pulp_result.remove(((clear_path, obf_path), value))
                    _related_sub_pulp_result[(clear_path[1:], obf_path[1:])] = value

            mapping_info.field_mapping = self.convert_pulp_result_to_field_mapping(
                sub_clear_msg, sub_obf_msg, _related_sub_pulp_result
            )

        return clear_by_obf_field_mapping

    def get_matrix_cost_between_field(
        self,
        clear_msg: PMessage,
        clear_elem_by_index: dict[int, PField | PMapField],
        obf_msg: PMessage,
        obf_elem_by_index: dict[int, PField | PMapField],
        reliability_by_indexes: dict[int, dict[int, float]],
        treated_clear_namespaces: set[str],
    ):
        """get matrix cost between each field, indexes of result need to be correlated"""
        cost_matrix = np.zeros((len(clear_elem_by_index), len(obf_elem_by_index)))
        clear_by_obf_mapping_by_indexes: dict[
            tuple[int, int],
            tuple[str, tuple[float, str, MappingInfo | None]],
        ] = {}

        for clear_index, clear_msg_elem in clear_elem_by_index.items():
            for obf_index, obf_msg_elem in obf_elem_by_index.items():
                if type(clear_msg_elem) is PField and type(obf_msg_elem) is PField:
                    cost_elem, sub_mapping_info = self.compare_p_field(
                        clear_msg,
                        clear_msg_elem,
                        obf_msg,
                        obf_msg_elem,
                        treated_clear_namespaces,
                    )
                elif (
                    type(clear_msg_elem) is PMapField
                    and type(obf_msg_elem) is PMapField
                ):
                    cost_elem, sub_mapping_info = self.compare_map_fields(
                        clear_msg,
                        clear_msg_elem,
                        obf_msg,
                        obf_msg_elem,
                        treated_clear_namespaces,
                    )
                else:
                    cost_elem = 0
                    sub_mapping_info = None

                clear_by_obf_mapping_by_indexes[(clear_index, obf_index)] = (
                    obf_msg_elem.name,
                    (cost_elem, clear_msg_elem.name, sub_mapping_info),
                )
                cost_matrix[clear_index, obf_index] = cost_elem * (
                    1 + math.log(reliability_by_indexes[clear_index][obf_index], 2)
                )

        return cost_matrix, clear_by_obf_mapping_by_indexes

    def compare_map_fields(
        self,
        clear_msg: PMessage,
        clear_p_map_field: PMapField,
        obf_msg: PMessage,
        obf_p_map_field: PMapField,
        treated_clear_namespaces: set[str],
    ) -> tuple[Percentage, MappingInfo | None]:
        if clear_p_map_field.key_type != obf_p_map_field.key_type:
            return 0, None

        return self.compare_p_field(
            clear_msg,
            clear_p_map_field.value_p_field,
            obf_msg,
            obf_p_map_field.value_p_field,
            treated_clear_namespaces,
        )

    @enforce_proxy_compare_field
    def compare_p_field(
        self,
        clear_msg: PMessage,
        clear_p_field: PField,
        obf_msg: PMessage,
        obf_p_field: PField,
        treated_clear_namespaces: set[str],
    ) -> tuple[Percentage, MappingInfo | None]:
        if (clear_p_field.cardinality is FieldCardinality.REPEATED) != (
            obf_p_field.cardinality is FieldCardinality.REPEATED
        ):
            return 0, None

        if (
            clear_p_field.type_name in PROTO_BASE_FIELDS
            or obf_p_field.type_name in PROTO_BASE_FIELDS
        ) and clear_p_field.type_name != obf_p_field.type_name:
            return 0, None

        related_validator = VALIDATORS_ON_FIELD.get(clear_msg.name)
        if related_validator:
            related_field_validators = related_validator.get(clear_p_field.name)
            if related_field_validators:
                is_respected = is_condition_respected(
                    obf_msg.namespace, obf_p_field.name, related_field_validators
                )
                if not is_respected:
                    return 0, None

        if clear_p_field.type_name in PROTO_BASE_FIELDS:
            assert (
                obf_p_field.type_name in PROTO_BASE_FIELDS
                and clear_p_field.type_name == obf_p_field.type_name
            )
            return 1, None

        clear_struct = ProtoOrganization.get_related_struct_from_type_name(
            self.clear_struct_by_namespace, clear_msg.namespace, clear_p_field.type_name
        )
        obf_struct = ProtoOrganization.get_related_struct_from_type_name(
            self.obf_struct_by_namespace, obf_msg.namespace, obf_p_field.type_name
        )
        if isinstance(clear_struct, PMessage) and isinstance(obf_struct, PMessage):
            if clear_struct.namespace in treated_clear_namespaces:
                return 1, None
            mapping_info = self.get_comparison_message(
                clear_struct,
                obf_struct,
                treated_clear_namespaces,
            )
            return mapping_info.similarity, mapping_info
        elif isinstance(clear_struct, PEnum) and isinstance(obf_struct, PEnum):
            return compare_p_enum(clear_struct, obf_struct), None

        return 0, None
