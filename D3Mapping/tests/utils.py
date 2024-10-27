from d3_mapping.mapping.proto_mapper import ProtoMapper
from d3_mapping.mapping.proto_organization import ProtoOrganization
from d3_mapping.models.p_message import PMessage

type ComparisonInfo = tuple[str, str]


def test_comparisons(p_mapper: ProtoMapper, comparisons: list[ComparisonInfo]):
    for comparison in comparisons:
        clear_namespace, obf_namespace = comparison
        clear_msg = p_mapper.clear_struct_by_namespace[clear_namespace]
        assert isinstance(clear_msg, PMessage)
        obf_msg = p_mapper.obf_struct_by_namespace[obf_namespace]
        assert isinstance(obf_msg, PMessage)
        mapping_info = p_mapper.get_comparison_message(
            clear_msg=clear_msg, obf_msg=obf_msg, treated_clear_namespaces=set()
        )

        clear_elem_by_index = ProtoOrganization.get_flat_elements(clear_msg)
        obf_elem_by_index = ProtoOrganization.get_flat_elements(obf_msg)
        reliability_by_indexes = (
            p_mapper.reliability_calculator.get_flat_reliability_by_indexes(
                clear_msg, obf_msg, set()
            )
        )

        cost_matrix, mapping_by_indexes = p_mapper.get_matrix_cost_between_field(
            clear_msg,
            clear_elem_by_index,
            obf_msg,
            obf_elem_by_index,
            reliability_by_indexes,
            set(),
        )

        print(mapping_info)
