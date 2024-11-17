from D3Mapping.d3_mapping.factories.p_namespace_factory import PNamespaceFactory
from D3Mapping.d3_mapping.mapping.global_proto_mapper import GlobalProtoMapper
from D3Mapping.d3_mapping.mapping.services.field_comparison_service import (
    FieldComparisonService,
)
from D3Mapping.d3_mapping.mapping.services.hungarian.cost_matrix_service import (
    CostMatrixService,
)
from D3Mapping.d3_mapping.mapping.services.hungarian.hungarian_solver_service import (
    HungarianSolverService,
)
from D3Mapping.d3_mapping.mapping.services.mapping_enforcement_service import (
    MappingEnforcementService,
)
from D3Mapping.d3_mapping.mapping.services.proto_reliability_calculator_service import (
    ProtoReliabilityCalculator,
)
from D3Mapping.d3_mapping.mapping.services.pulp.deep_mapping_data_service import (
    DeepMappingDataService,
)
from D3Mapping.d3_mapping.mapping.services.pulp.pulp_result_converter import (
    PulpResultConverter,
)
from D3Mapping.d3_mapping.mapping.services.pulp.pulp_solver_service import (
    PulpSolverService,
)
from D3Mapping.d3_mapping.mapping.validators.proto_validator import ProtoValidator
from D3Mapping.d3_mapping.models.mapping_metrics import MappingMetrics
from D3Mapping.d3_mapping.models.verified_mapping import VerifiedMapping


class PMapperFactory:
    @staticmethod
    def create_p_mapper(
        clear_directory: str,
        obf_directory: str,
        verified_mapping: VerifiedMapping,
    ):
        _, clear_struct_by_namespace = PNamespaceFactory.create_namespace_on_directory(
            clear_directory
        )
        obf_root_msgs, obf_struct_by_namespace = (
            PNamespaceFactory.create_namespace_on_directory(obf_directory)
        )
        obf_root_namespaces = [
            obf_root_name
            for obf_root_names in obf_root_msgs.values()
            for obf_root_name in obf_root_names
        ]
        print(f"Getting mapping for clear directory : {clear_directory}")
        reliability_calculator = ProtoReliabilityCalculator(
            clear_struct_by_namespace=clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
            verified_obf_msg_name_by_clear_msg_name=verified_mapping.verified_msg_by_obf,
        )
        msg_mapping_info_by_obf_namespace = {}
        proto_validator = ProtoValidator(
            clear_struct_by_namespace=clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
            msg_mapping_info_by_obf_namespace=msg_mapping_info_by_obf_namespace,
        )
        metrics = MappingMetrics()
        added_mapping_by_obf_namespaces = {}
        mapping_enforcement_service = MappingEnforcementService(
            verified_msg_by_obf=verified_mapping.verified_msg_by_obf,
            verified_msg_by_clear={
                value: key
                for key, value in verified_mapping.verified_msg_by_obf.items()
            },
            verified_mapping_field_by_clear=verified_mapping.field_mappings,
            added_mapping_by_obf_namespaces=added_mapping_by_obf_namespaces,
            metrics=metrics,
        )
        field_comparison_service = FieldComparisonService(
            mapping_enforcement_service=mapping_enforcement_service,
            clear_struct_by_namespace=clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
        )
        deep_mapping_data_service = DeepMappingDataService(
            clear_struct_by_namespace=clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
            reliability_calculator=reliability_calculator,
            field_comparison_service=field_comparison_service,
        )
        pulp_result_converter = PulpResultConverter(
            clear_struct_by_namespace=clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
        )
        pulp_solver_service = PulpSolverService(
            metrics=metrics,
            proto_validator=proto_validator,
            deep_mapping_data_service=deep_mapping_data_service,
            pulp_result_converter=pulp_result_converter,
        )
        cost_matrix_service = CostMatrixService(
            field_comparison_service=field_comparison_service,
            reliability_calculator=reliability_calculator,
        )
        hungarian_solver_service = HungarianSolverService(
            cost_matrix_service=cost_matrix_service,
        )
        proto_mapper = GlobalProtoMapper(
            clear_struct_by_namespace=clear_struct_by_namespace,
            obf_struct_by_namespace=obf_struct_by_namespace,
            obf_root_namespaces=obf_root_namespaces,
            verified_msg_by_obf=verified_mapping.verified_msg_by_obf,
            msg_mapping_info_by_clear_namespace=msg_mapping_info_by_obf_namespace,
            metrics=metrics,
            pulp_solver_service=pulp_solver_service,
            hungarian_solver_service=hungarian_solver_service,
            mapping_enforcement_service=mapping_enforcement_service,
            added_mapping_by_obf_namespaces=added_mapping_by_obf_namespaces,
        )
        return proto_mapper
