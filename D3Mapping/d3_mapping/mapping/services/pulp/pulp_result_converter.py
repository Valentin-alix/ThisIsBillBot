from dataclasses import dataclass

from D3Mapping.d3_mapping.mapping.services.proto_organization_service import (
    ProtoOrganization,
)
from D3Mapping.d3_mapping.models.mapping_info import FieldMapping, MappingInfo
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import PMessage

PulpMappingStruct = dict[tuple[tuple[str, ...], tuple[str, ...]], float]


@dataclass
class PulpResultConverter:
    """Service for converting PuLP optimization results to field mappings."""

    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]

    def convert(
        self, clear_msg: PMessage, obf_msg: PMessage, pulp_result: PulpMappingStruct
    ) -> FieldMapping:
        """Convert PuLP result to hierarchical field mapping.

        Takes the flat PuLP optimization result (paths with similarity scores)
        and converts it into a nested FieldMapping structure.

        Args:
            clear_msg: Clear message
            obf_msg: Obfuscated message
            pulp_result: PuLP result with (clear_path, obf_path) -> similarity

        Returns:
            Hierarchical FieldMapping
        """
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
                    None,
                )
                sorted_pulp_result.pop(0)
                continue

            if prefix_obf_path not in clear_by_obf_field_mapping:
                return {}

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

            mapping_info.field_mapping = self.convert(
                sub_clear_msg, sub_obf_msg, _related_sub_pulp_result
            )

        return clear_by_obf_field_mapping
