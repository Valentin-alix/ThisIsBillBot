from D3Mapping.d3_mapping.factories.p_namespace_factory import PNamespaceFactory
from D3Mapping.d3_mapping.mapping.proto_mapper import ProtoMapper
from D3Mapping.d3_mapping.mapping.proto_reliability_calculator import (
    ProtoReliabilityCalculator,
)
from D3Mapping.d3_mapping.mapping.validators.proto_validator import ProtoValidator


class PMapperFactory:
    @staticmethod
    def create_p_mapper(
        clear_directory: str,
        obf_directory: str,
        verified_mapping_by_obf: dict[str, str],
        verified_mapping_fields: dict[str, dict[str, str]],
    ):
        clear_root_msgs, clear_struct_by_namespace = (
            PNamespaceFactory.create_namespace_on_directory(clear_directory)
        )
        obf_root_msgs, obf_struct_by_namespace = (
            PNamespaceFactory.create_namespace_on_directory(obf_directory)
        )
        obf_root_namespaces = [
            obf_root_name
            for obf_root_names in obf_root_msgs.values()
            for obf_root_name in obf_root_names
        ]
        clear_root_namespaces = [
            clear_root_name
            for clear_root_names in clear_root_msgs.values()
            for clear_root_name in clear_root_names
        ]
        print(f"Getting mapping for clear directory : {clear_directory}")
        reliability_calculator = ProtoReliabilityCalculator(
            clear_struct_by_namespace=clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
            verified_obf_msg_name_by_clear_msg_name=verified_mapping_by_obf,
        )
        msg_mapping_info_by_obf_namespace = {}
        proto_validator = ProtoValidator(
            clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
            msg_mapping_info_by_obf_namespace=msg_mapping_info_by_obf_namespace,
        )
        proto_mapper = ProtoMapper(
            proto_validator=proto_validator,
            clear_struct_by_namespace=clear_struct_by_namespace,
            clear_root_namespaces=clear_root_namespaces,
            obf_struct_by_namespace=obf_struct_by_namespace,
            obf_root_namespaces=obf_root_namespaces,
            reliability_calculator=reliability_calculator,
            verified_msg_by_obf=verified_mapping_by_obf,
            verified_mapping_field_by_clear=verified_mapping_fields,
            msg_mapping_info_by_obf_namespace=msg_mapping_info_by_obf_namespace,
        )
        return proto_mapper
