from dataclasses import dataclass
from typing import Callable

from proto_schema_parser import FieldCardinality

from D3Mapping.d3_mapping.consts import PROTO_BASE_FIELDS
from D3Mapping.d3_mapping.mapping.services.enum_comparison_service import compare_p_enum
from D3Mapping.d3_mapping.mapping.services.mapping_enforcement_service import MappingEnforcementService
from D3Mapping.d3_mapping.mapping.services.proto_organization_service import ProtoOrganization
from D3Mapping.d3_mapping.mapping.validators.field_validators import VALIDATORS_ON_FIELD
from D3Mapping.d3_mapping.mapping.validators.proto_field_validators import is_condition_respected
from D3Mapping.d3_mapping.models.mapping_info import MappingInfo, Percentage, RejectionReason
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import PField, PMapField, PMessage


@dataclass
class FieldComparisonResult:
    """Result of comparing two fields."""

    similarity: Percentage
    mapping_info: MappingInfo | None
    rejection_reason: RejectionReason | None = None


@dataclass
class FieldComparisonService:
    mapping_enforcement_service: MappingEnforcementService
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    """Service for comparing individual protobuf fields.

    This service handles the comparison logic for PField and PMapField,
    extracting this responsibility from ComparisonEngine.
    """

    def compare_elements(
        self,
        compare_msg: Callable,
        clear_msg: PMessage,
        clear_elem: PField | PMapField,
        obf_msg: PMessage,
        obf_elem: PField | PMapField,
        treated_clear_namespaces: set[str],
    ) -> FieldComparisonResult:
        """Helper method to compare individual elements"""
        if type(clear_elem) is PField and type(obf_elem) is PField:
            sim, mapping_info, rejection_reason = self.compare_p_field(
                compare_msg,
                clear_msg,
                clear_elem,
                obf_msg,
                obf_elem,
                treated_clear_namespaces,
            )
        elif type(clear_elem) is PMapField and type(obf_elem) is PMapField:
            sim, mapping_info, rejection_reason = self.compare_map_fields(
                compare_msg,
                clear_msg,
                clear_elem,
                obf_msg,
                obf_elem,
                treated_clear_namespaces,
            )
        else:
            sim, mapping_info, rejection_reason = 0, None, RejectionReason.TYPE_MISMATCH

        return FieldComparisonResult(
            similarity=sim, mapping_info=mapping_info, rejection_reason=rejection_reason
        )

    def compare_map_fields(
        self,
        compare_msg: Callable,
        clear_msg: PMessage,
        clear_p_map_field: PMapField,
        obf_msg: PMessage,
        obf_p_map_field: PMapField,
        treated_clear_namespaces: set[str],
    ) -> tuple[Percentage, MappingInfo | None, RejectionReason | None]:
        if clear_p_map_field.key_type != obf_p_map_field.key_type:
            return 0, None, RejectionReason.TYPE_MISMATCH

        return self.compare_p_field(
            compare_msg,
            clear_msg,
            clear_p_map_field.value_p_field,
            obf_msg,
            obf_p_map_field.value_p_field,
            treated_clear_namespaces,
        )

    def compare_p_field(
        self,
        compare_msg: Callable,
        clear_msg: PMessage,
        clear_p_field: PField,
        obf_msg: PMessage,
        obf_p_field: PField,
        treated_clear_namespaces: set[str],
    ) -> tuple[Percentage, MappingInfo | None, RejectionReason | None]:
        if (clear_p_field.cardinality is FieldCardinality.REPEATED) != (
            obf_p_field.cardinality is FieldCardinality.REPEATED
        ):
            return 0, None, RejectionReason.CARDINALITY_MISMATCH

        if (
            clear_p_field.type_name in PROTO_BASE_FIELDS or obf_p_field.type_name in PROTO_BASE_FIELDS
        ) and clear_p_field.type_name != obf_p_field.type_name:
            return 0, None, RejectionReason.TYPE_MISMATCH

        related_validator = VALIDATORS_ON_FIELD.get(clear_msg.name)
        if related_validator:
            related_field_validators = related_validator.get(clear_p_field.name)
            if related_field_validators:
                is_respected = is_condition_respected(obf_msg.namespace, obf_p_field.name, related_field_validators)
                if not is_respected:
                    return 0, None, RejectionReason.VALIDATOR_FAILURE

        if clear_p_field.type_name in PROTO_BASE_FIELDS:
            assert obf_p_field.type_name in PROTO_BASE_FIELDS and clear_p_field.type_name == obf_p_field.type_name
            return 1, None, None

        clear_struct = ProtoOrganization.get_related_struct_from_type_name(
            self.clear_struct_by_namespace, clear_msg.namespace, clear_p_field.type_name
        )
        obf_struct = ProtoOrganization.get_related_struct_from_type_name(
            self.obf_struct_by_namespace, obf_msg.namespace, obf_p_field.type_name
        )
        if isinstance(clear_struct, PMessage) and isinstance(obf_struct, PMessage):
            if clear_struct.namespace in treated_clear_namespaces:
                return 1, None, None
            mapping_info = compare_msg(
                clear_struct,
                obf_struct,
                treated_clear_namespaces,
            )
            sim, mapping_info = mapping_info.similarity, mapping_info
        elif isinstance(clear_struct, PEnum) and isinstance(obf_struct, PEnum):
            sim, mapping_info = compare_p_enum(clear_struct, obf_struct), None
        else:
            return 0, None, RejectionReason.TYPE_MISMATCH

        return self.mapping_enforcement_service.enforce_field_comparison(
            sim, mapping_info, clear_msg, clear_p_field, obf_p_field
        )
