from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
from proto_schema_parser import FieldCardinality
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm

from d3_mapping.controller.instancied_msg_info_controller import (
    MSG_INFO_BY_NAME,
)
from d3_mapping.mapping.consts import LIMIT, PROTO_BASE_FIELDS, EntryMsg
from d3_mapping.mapping.legacy.legacy_proto_reliability_calculator import (
    LegacyProtoReliabilityCalculator,
)
from d3_mapping.mapping.proto_organization import ProtoOrganization
from d3_mapping.mapping.validators.proto_field_validators import (
    VALIDATORS_ON_FIELD,
    is_condition_respected,
    is_parsed_obf_msg,
)
from d3_mapping.models.mapping_info import FieldMapping, OutputMappingInfo
from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import (
    PField,
    PMapField,
    PMessage,
)
from d3_mapping.utils import Percentage, set_percentage


@dataclass
class LegacyProtoMapper:
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    clear_root_namespace_by_filename: dict[str, list[str]]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_root_namespaces: list[str]
    reliability_calculator: LegacyProtoReliabilityCalculator

    msg_info_by_namespace: defaultdict[
        str,
        dict[str, tuple[float, FieldMapping]],
    ] = field(init=False, default_factory=lambda: defaultdict(dict))
    enum_sim_by_namespace: defaultdict[str, dict[str, float]] = field(
        init=False, default_factory=lambda: defaultdict(dict)
    )
    msg_mapping_info_by_obf_name: dict[str, OutputMappingInfo] = field(
        init=False, default_factory=dict
    )
    mapped_by_clear_namespace: dict[str, str] = field(init=False, default_factory=dict)
    enum_mapping_by_obf_name: dict[str, str] = field(init=False, default_factory=dict)

    verified_mapping_by_obf: dict[str, str]
    verified_mapping_by_clear: dict[str, str]
    verified_mapping_fields: dict[str, dict[str, str]]

    def run_mapping(self) -> dict[str, OutputMappingInfo]:
        # because new proto message is on only one file
        self.obf_root_namespaces.sort()

        # here we sort proto file by most reliable msg because order INSIDE old file info is kept
        sorted_clear_files = (
            self.reliability_calculator.get_sorted_clear_files_by_reliability()
        )

        for clear_filename, clear_sorted_msgs in tqdm(sorted_clear_files):
            # get most similar msg for most reliable msg to check on order after
            reliable_mapping_with_indexes: (
                tuple[PMessage, int, PMessage, int] | None
            ) = None
            for clear_index, clear_msg, _ in clear_sorted_msgs:
                obf_msgs_to_lookup = (
                    (obf_index, obf_struct)
                    for obf_index, obf_namespace in enumerate(self.obf_root_namespaces)
                    if obf_namespace not in self.msg_mapping_info_by_obf_name
                    and isinstance(
                        (obf_struct := self.obf_struct_by_namespace[obf_namespace]),
                        PMessage,
                    )
                )
                obf_reliable_index, obf_struct, (sim, _) = max(
                    (
                        (
                            obf_index,
                            obf_struct,
                            (
                                self.get_comparison_message(
                                    clear_msg.namespace, obf_struct.namespace, set()
                                )[0],
                                self.reliability_calculator.get_reliability_clear_message(
                                    clear_msg, obf_struct, set()
                                ),
                            ),
                        )
                        for obf_index, obf_struct in obf_msgs_to_lookup
                    ),
                    key=lambda info: (info[2]),
                )
                if sim >= LIMIT:
                    reliable_mapping_with_indexes = (
                        clear_msg,
                        clear_index,
                        obf_struct,
                        obf_reliable_index,
                    )
                    break

            if not reliable_mapping_with_indexes:
                continue

            (
                clear_reliable_msg,
                clear_reliable_index,
                obf_reliable_msg,
                obf_reliable_index,
            ) = reliable_mapping_with_indexes

            # print(f"{clear_filename} found most reliable {clear_reliable_msg.name}")

            self.add_new_msg_mapping(clear_reliable_msg, obf_reliable_msg, set())

            # here we gonna find the best combination that gives the best similarity overall
            cost_matrix = self.get_matrix_cost_in_range_for_file(
                clear_reliable_index, obf_reliable_index, clear_filename
            )
            clear_indexes, obf_indexes = linear_sum_assignment(
                cost_matrix, maximize=True
            )
            for clear_index, obf_index in zip(clear_indexes, obf_indexes):
                sim = cost_matrix[clear_index, obf_index].sum()
                if sim == 0:
                    continue

                clear_namespace: str = self.clear_root_namespace_by_filename[
                    clear_filename
                ][clear_index]
                obf_namespace: str = self.obf_root_namespaces[obf_index]
                sim = self.get_comparison_message(
                    clear_namespace, obf_namespace, set()
                )[0]

                if sim < LIMIT:
                    continue

                clear_msg = self.clear_struct_by_namespace[clear_namespace]
                assert isinstance(clear_msg, PMessage)

                obf_msg = self.obf_struct_by_namespace[obf_namespace]
                assert isinstance(obf_msg, PMessage)

                self.add_new_msg_mapping(clear_msg, obf_msg, set())

        unmapped_obf_name = [
            obf_name
            for obf_name in self.obf_root_namespaces
            if obf_name not in self.msg_mapping_info_by_obf_name
            and isinstance(self.obf_struct_by_namespace[obf_name], PMessage)
        ]

        print(f"Unmapped obf msg name : {unmapped_obf_name}")

        unmapped_clear_name = [
            namespace
            for namespaces in self.clear_root_namespace_by_filename.values()
            for namespace in namespaces
            if namespace not in self.mapped_by_clear_namespace
            and isinstance(self.clear_struct_by_namespace[namespace], PMessage)
        ]

        print(f"Unmapped clear msg name : {unmapped_clear_name}")

        return self.msg_mapping_info_by_obf_name

    def get_matrix_cost_in_range_for_file(
        self, clear_reliable_index: int, obf_reliable_index: int, clear_filename: str
    ):
        in_range_namespaces = [
            (index, namespace)
            for index, namespace in enumerate(self.obf_root_namespaces)
            if namespace not in self.msg_mapping_info_by_obf_name
            and abs(obf_reliable_index - index)
            <= len(self.clear_root_namespace_by_filename[clear_filename]) * 1.5
            and isinstance(self.obf_struct_by_namespace[namespace], PMessage)
        ]

        cost_matrix = np.zeros(
            (
                len(self.clear_root_namespace_by_filename[clear_filename]),
                len(self.obf_root_namespaces),
            )
        )
        for clear_index, clear_namespace in enumerate(
            self.clear_root_namespace_by_filename[clear_filename]
        ):
            clear_struct = self.clear_struct_by_namespace[clear_namespace]
            if not isinstance(clear_struct, PMessage):
                continue
            if clear_struct.name in self.verified_mapping_by_clear:
                if (
                    self.verified_mapping_by_clear[clear_struct.name]
                    not in self.obf_root_namespaces
                ):
                    continue

                in_range_namespaces.append(
                    (
                        self.obf_root_namespaces.index(
                            self.verified_mapping_by_clear[clear_struct.name]
                        ),
                        self.verified_mapping_by_clear[clear_struct.name],
                    )
                )
            for obf_index, obf_namespace in in_range_namespaces:
                obf_struct = self.obf_struct_by_namespace[obf_namespace]
                if not isinstance(obf_struct, PMessage):
                    continue

                sim = self.get_comparison_message(
                    clear_namespace, obf_namespace, set()
                )[0]
                if sim < LIMIT:
                    continue

                reliability = self.reliability_calculator.get_reliability_clear_message(
                    clear_struct, obf_struct, set()
                )
                diff_index = abs(
                    (obf_reliable_index - obf_index)
                    - (clear_reliable_index - clear_index)
                )
                cost_matrix[clear_index, obf_index] = (
                    sim + (reliability / 1_000_000) - (diff_index / 10_000_000)
                )

        return cost_matrix

    def add_new_msg_mapping(
        self, clear_msg: PMessage, obf_msg: PMessage, treated_namespace: set[str]
    ):
        if (
            obf_msg.namespace in self.msg_mapping_info_by_obf_name
            or clear_msg.namespace in self.mapped_by_clear_namespace
        ):
            return

        sim, field_mapping = self.get_comparison_message(
            clear_msg.namespace, obf_msg.namespace, set()
        )

        self.msg_mapping_info_by_obf_name[obf_msg.namespace] = OutputMappingInfo(
            clear_msg_namespace=clear_msg.namespace,
            similarity=sim,
            field_mapping=field_mapping,
        )
        self.mapped_by_clear_namespace[clear_msg.namespace] = obf_msg.namespace

        # also add on mapping sub namespaces
        treated_namespace = treated_namespace.copy()
        treated_namespace.add(clear_msg.namespace)

        obf_flat_elements = ProtoOrganization.get_flat_elements(obf_msg.elements)[
            1
        ].values()
        for clear_elem in ProtoOrganization.get_flat_elements(clear_msg.elements)[
            1
        ].values():
            clear_type_name = (
                clear_elem.value_p_field.type_name
                if isinstance(clear_elem, PMapField)
                else clear_elem.type_name
            )
            if clear_type_name in PROTO_BASE_FIELDS:
                continue

            if clear_elem.name not in field_mapping:
                continue
            related_obf_field_name = field_mapping[clear_elem.name][0]
            related_obf_elem = next(
                elem
                for elem in obf_flat_elements
                if elem.name == related_obf_field_name
            )
            obf_type_name = (
                related_obf_elem.value_p_field.type_name
                if isinstance(related_obf_elem, PMapField)
                else related_obf_elem.type_name
            )
            if obf_type_name in PROTO_BASE_FIELDS:
                continue

            sub_clear_nested_namespace = f"{clear_msg.namespace}.{clear_type_name}"
            sub_clear_namespace = (
                sub_clear_nested_namespace
                if sub_clear_nested_namespace in self.clear_struct_by_namespace
                else clear_type_name
            )
            if sub_clear_namespace in treated_namespace:
                continue

            sub_obf_nested_namespace = f"{obf_msg.namespace}.{obf_type_name}"
            sub_obf_namespace = (
                sub_obf_nested_namespace
                if sub_obf_nested_namespace in self.obf_struct_by_namespace
                else obf_type_name
            )

            sub_clear_struct = self.clear_struct_by_namespace[sub_clear_namespace]
            sub_obf_struct = self.obf_struct_by_namespace[sub_obf_namespace]

            if isinstance(sub_clear_struct, PEnum) and isinstance(
                sub_obf_struct, PEnum
            ):
                self.add_new_enum_mapping(sub_clear_struct, sub_obf_struct)
            elif isinstance(sub_clear_struct, PMessage) and isinstance(
                sub_obf_struct, PMessage
            ):
                self.add_new_msg_mapping(
                    sub_clear_struct, sub_obf_struct, treated_namespace
                )

    def add_new_enum_mapping(self, clear_enum: PEnum, obf_enum: PEnum):
        self.enum_mapping_by_obf_name[obf_enum.namespace] = clear_enum.namespace

    def get_comparison_message(
        self,
        clear_namespace: str,
        obf_namespace: str,
        treated_msg_namespaces: set[str],
    ) -> tuple[Percentage, FieldMapping]:
        clear_msg = self.clear_struct_by_namespace[clear_namespace]
        assert isinstance(clear_msg, PMessage)

        obf_msg = self.obf_struct_by_namespace[obf_namespace]
        assert isinstance(obf_msg, PMessage)

        def proxy_comparison_msg(
            clear_namespace: str,
            obf_namespace: str,
            sim: Percentage,
            sim_by_fields: FieldMapping,
        ):
            if clear_msg.name in self.verified_mapping_by_clear:
                sim = (
                    0
                    if obf_msg.name != self.verified_mapping_by_clear[clear_msg.name]
                    else 1
                )
            if obf_msg.name in self.verified_mapping_by_obf:
                sim = (
                    0
                    if clear_msg.name != self.verified_mapping_by_obf[obf_msg.name]
                    else 1
                )

            self.msg_info_by_namespace[clear_namespace][obf_namespace] = (
                set_percentage(sim),
                sim_by_fields,
            )
            return self.msg_info_by_namespace[clear_namespace][obf_namespace]

        if (
            obf_msg.namespace in self.msg_mapping_info_by_obf_name
            and self.msg_mapping_info_by_obf_name[obf_msg.namespace].clear_msg_namespace
            != clear_msg.namespace
        ):
            return 0, {}

        if (
            clear_msg.namespace in self.mapped_by_clear_namespace
            and self.mapped_by_clear_namespace[clear_msg.namespace] != obf_msg.namespace
        ):
            return 0, {}

        if obf_msg.namespace in self.msg_info_by_namespace[clear_msg.namespace]:
            return self.msg_info_by_namespace[clear_msg.namespace][obf_msg.namespace]

        if (
            is_parsed_obf_msg(obf_msg.name)
            and MSG_INFO_BY_NAME[obf_msg.name].is_entry_msg
        ):
            if not any(
                clear_msg.name.endswith(entry_msg_name) for entry_msg_name in EntryMsg
            ):
                # clear msg is not entry msg (event, request, response) but obf is an entry msg)
                return proxy_comparison_msg(
                    clear_msg.namespace, obf_msg.namespace, 0, {}
                )

            if (
                clear_msg.name.endswith(EntryMsg.REQUEST)
                and MSG_INFO_BY_NAME[obf_msg.name].from_server
            ) or (
                (
                    clear_msg.name.endswith(EntryMsg.RESPONSE)
                    or clear_msg.name.endswith(EntryMsg.EVENT)
                )
                and not MSG_INFO_BY_NAME[obf_msg.name].from_server
            ):
                return proxy_comparison_msg(
                    clear_msg.namespace, obf_msg.namespace, 0, {}
                )

        if len(clear_msg.elements) == 0:
            if len(obf_msg.elements) == 0:
                return proxy_comparison_msg(
                    clear_msg.namespace, obf_msg.namespace, 1, {}
                )
            return proxy_comparison_msg(clear_msg.namespace, obf_msg.namespace, 0, {})
        if len(obf_msg.elements) == 0:
            return proxy_comparison_msg(clear_msg.namespace, obf_msg.namespace, 0, {})

        treated_msg_namespaces = treated_msg_namespaces.copy()
        treated_msg_namespaces.add(clear_msg.namespace)

        reliability_by_indexes = self.reliability_calculator.get_reliability_by_indexes(
            clear_msg, obf_msg, treated_msg_namespaces
        )
        len_clear_elems, clear_elem_by_index = ProtoOrganization.get_flat_elements(
            clear_msg.elements
        )
        len_obf_elems, obf_elem_by_index = ProtoOrganization.get_flat_elements(
            obf_msg.elements
        )

        cost_matrix, sim_by_indexes = self.get_matrix_cost_between_field(
            len_clear_elems,
            clear_elem_by_index,
            clear_msg,
            len_obf_elems,
            obf_elem_by_index,
            obf_msg,
            reliability_by_indexes,
            treated_msg_namespaces,
        )
        row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)

        sim_by_fields: FieldMapping = {}
        total_reliability: float = 0
        for i, j in zip(row_ind, col_ind):
            clear_field_name, obf_field_name, field_sim = sim_by_indexes[(i, j)]
            sim_by_fields[clear_field_name] = (obf_field_name, field_sim)
            total_reliability += reliability_by_indexes[i][j]

        # validator_on_whole_msg = VALIDATORS_ON_SET_FIELDS.get(clear_msg.name)
        # if validator_on_whole_msg and (
        #     parsed_obf_msg_infos := MSG_INFO_BY_NAME.get(obf_msg.name)
        # ):
        #     for obf_msg_info in parsed_obf_msg_infos.obf_msg_info:
        #         value_by_field_mapped_to_clear = {obf_msg_info.value_by_field_array.items()}
        #     validator_on_whole_msg()
        # # Check la validity, si pas valide mettre un malus

        if total_reliability == 0:
            return proxy_comparison_msg(clear_msg.namespace, obf_msg.namespace, 0, {})

        msg_sim = cost_matrix[row_ind, col_ind].sum() / total_reliability

        msg_sim = self.get_value_with_len_malus(msg_sim, len_clear_elems, len_obf_elems)

        # assembly mapping is not efficient enough
        # sim_from_assembly = self.proto_mapper_assembly.compare_structs(
        #     obf_msg.namespace, clear_msg.namespace
        # )
        # if sim_from_assembly is not None:
        #     msg_sim = (msg_sim + sim_from_assembly) / 2

        return proxy_comparison_msg(
            clear_msg.namespace, obf_msg.namespace, msg_sim, sim_by_fields
        )

    def get_matrix_cost_between_field(
        self,
        len_clear_elems: int,
        clear_elem_by_index: dict[int, PField | PMapField],
        clear_msg: PMessage,
        len_obf_elems: int,
        obf_elem_by_index: dict[int, PField | PMapField],
        obf_msg: PMessage,
        reliability_by_indexes: dict[int, dict[int, float]],
        treated_msg_namespaces: set[str],
    ) -> tuple[
        np.ndarray[tuple[int, int], np.dtype[np.float64]],
        dict[tuple[int, int], tuple[str, str, Percentage]],
    ]:
        """get matrix cost between each field, indexes of result need to be correlated"""
        cost_matrix = np.zeros((len_clear_elems, len_obf_elems))
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
            clear_msg.name in self.verified_mapping_fields
            and clear_p_field.name in self.verified_mapping_fields[clear_msg.name]
        ):
            if (
                self.verified_mapping_fields[clear_msg.name][clear_p_field.name]
                == obf_p_field.name
            ):
                return 1
            return 0

        if (clear_p_field.cardinality is FieldCardinality.REPEATED) != (
            obf_p_field.cardinality is FieldCardinality.REPEATED
        ):
            return 0

        if clear_p_field.type_name in PROTO_BASE_FIELDS:
            if clear_p_field.type_name != obf_p_field.type_name:
                return 0
            related_validator = VALIDATORS_ON_FIELD.get(clear_msg.name)

            if related_validator:
                related_field_validators = related_validator.get(clear_p_field.name)
                if related_field_validators:
                    is_respected, value = is_condition_respected(
                        obf_msg.namespace, obf_p_field.name, related_field_validators
                    )
                    if not is_respected:
                        # if obf_p_field.name == "egwd" and clear_p_field.name == "types":
                        #     print(
                        #         f"Condition not respected for value {value} {obf_msg.namespace} {related_field_validators}"
                        #     )
                        return 0

            return 1

        if obf_p_field.type_name in PROTO_BASE_FIELDS:
            return 0

        clear_struct = ProtoOrganization.get_related_struct_from_type_name(
            self.clear_struct_by_namespace, clear_msg.namespace, clear_p_field.type_name
        )
        obf_struct = ProtoOrganization.get_related_struct_from_type_name(
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
        if obf_enum.namespace in self.enum_mapping_by_obf_name:
            mapped_clear_namespace = self.enum_mapping_by_obf_name[obf_enum.namespace]
            if mapped_clear_namespace != clear_enum.namespace:
                return 0
            return 1

        if obf_enum.namespace in self.enum_sim_by_namespace[clear_enum.namespace]:
            return self.enum_sim_by_namespace[clear_enum.namespace][obf_enum.namespace]

        self.enum_sim_by_namespace[clear_enum.namespace][obf_enum.namespace] = (
            self.get_value_with_len_malus(
                1, len(clear_enum.elements), len(obf_enum.elements)
            )
        )
        return self.enum_sim_by_namespace[clear_enum.namespace][obf_enum.namespace]

    def get_value_with_len_malus(
        self, value: float, len_clear_elems: int, len_obf_elems: int
    ) -> float:
        malus = 2 if len_clear_elems > len_obf_elems else 1
        if len_obf_elems - 1 == len_clear_elems:
            return value / 1.1

        min_len_elems = min(len_clear_elems, len_obf_elems)
        max_len_elems = max(len_clear_elems, len_obf_elems)
        return value * (min_len_elems / max_len_elems) / malus
