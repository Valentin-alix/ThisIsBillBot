import numpy as np
import pytest

from DBDofusUnity.proto_mapper_assembly.field_mapping.pulp.solver import solve_field_mapping_ilp
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from tests.fixtures.proto_mapper.field_builders import scalar_field
from tests.fixtures.proto_mapper.message_builders import (
    make_field_mapping_context,
    make_message_signature,
    prepare_field_mapping_context_for_test,
)


@pytest.mark.parametrize(
    ("runtime_instances", "expected_pairs"),
    [
        ((), {(0, 0), (1, 1)}),
        (({"a": 50, "b": 100},), {(0, 1), (1, 0)}),
    ],
)
def test_ilp_assignment_respects_runtime_constraints(
    runtime_instances: tuple[dict[str, object], ...],
    expected_pairs: set[tuple[int, int]],
) -> None:
    non_obf = DumpCSMessage(
        file_descriptor="GameReflection",
        name="UpdateLifePointsEvent",
        fields=[scalar_field("max_life_points_", 16), scalar_field("life_points_", 20)],
    )
    obf = DumpCSMessage(
        file_descriptor="GameReflection",
        name="obf",
        fields=[scalar_field("a_", 16), scalar_field("b_", 20)],
    )
    for message in (non_obf, obf):
        for field in message.fields:
            field.property_name = field.clean_field_name
    context = prepare_field_mapping_context_for_test(
        non_obf_signature=make_message_signature(
            non_obf, live_field_keys=frozenset(field.field_key for field in non_obf.fields)
        ),
        obf_signature=make_message_signature(
            obf, live_field_keys=frozenset(field.field_key for field in obf.fields)
        ),
        field_mapping_context=make_field_mapping_context(RuntimeDataStore()),
    )

    result = solve_field_mapping_ilp(
        context=context,
        similarity_matrix=np.array([[10.0, 9.0], [9.0, 10.0]]),
        runtime_instances=runtime_instances,
    )

    assert result is not None
    assert set(zip(result[0].tolist(), result[1].tolist(), strict=True)) == expected_pairs
