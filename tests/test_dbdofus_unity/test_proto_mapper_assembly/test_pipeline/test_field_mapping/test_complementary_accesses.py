import pytest

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from tests.fixtures.proto_mapper.field_builders import dump_field
from tests.fixtures.proto_mapper.message_builders import (
    build_field_mapping_for_test,
    make_field_mapping_context,
)
from tests.fixtures.proto_mapper.signatures import access_atom, field_access_signature


@pytest.mark.parametrize("ambiguous_side", [None, "left", "right"])
def test_complementary_traces_require_a_unique_scalar_pair(
    runtime_data_store: RuntimeDataStore,
    ambiguous_side: str | None,
) -> None:
    signatures: list[MessageAccessSignature] = []
    for side, kind in (("left", "read"), ("right", "write")):
        fields = [dump_field(f"{side}_id_", f"{side.title()}Id", 24, FieldCategoryEnum.NUMBER)]
        if ambiguous_side == side:
            fields.append(dump_field("other_id_", "OtherId", 28, FieldCategoryEnum.NUMBER))
        message = DumpCSMessage(file_descriptor="Group", name=side, fields=fields)
        signatures.append(
            MessageAccessSignature(
                message_cls=side,
                file_descriptor="Group",
                dump_cs_msg=message,
                function_signatures=[],
                field_signatures=[
                    field_access_signature(
                        field_key=field.field_key,
                        field_type_shape=field.field_type_shape,
                        accesses=[access_atom(access_kind=kind, field_type_shape=field.field_type_shape)],
                    )
                    for field in fields
                ],
            )
        )
    left, right = signatures
    result = build_field_mapping_for_test(
        non_obf_signature=left,
        obf_signature=right,
        non_obf_messages_by_cls={"left": left.dump_cs_msg},
        obf_messages_by_cls={"right": right.dump_cs_msg},
        field_mapping_context=make_field_mapping_context(runtime_data_store),
    )
    assert result.field_mapping == ({"right_id": "left_id"} if ambiguous_side is None else {})
