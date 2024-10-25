from d3_mapping.mapping.proto_mapper import ProtoMapper
from d3_mapping.models.p_message import PMessage

type ComparisonInfo = tuple[str, str, float | None, float | None]


def test_comparisons(p_mapper: ProtoMapper, comparisons: list[ComparisonInfo]):
    for comparison in comparisons:
        clear_namespace, obf_namespace, min_sim, max_sim = comparison
        clear_msg = p_mapper.clear_struct_by_namespace[clear_namespace]
        assert isinstance(clear_msg, PMessage)
        obf_msg = p_mapper.obf_struct_by_namespace[obf_namespace]
        assert isinstance(obf_msg, PMessage)
        similarity, field_mapping = p_mapper.get_comparison_message(
            clear_namespace=clear_namespace,
            obf_namespace=obf_namespace,
            treated_msg_namespaces=set(),
        )
        reliability = p_mapper.reliability_calculator.get_reliability_clear_message(
            clear_msg, obf_msg, set()
        )
        if min_sim is not None:
            assert similarity >= min_sim
        if max_sim is not None:
            assert similarity <= max_sim

        if min_sim is None and max_sim is None:
            print(similarity, reliability, field_mapping)
