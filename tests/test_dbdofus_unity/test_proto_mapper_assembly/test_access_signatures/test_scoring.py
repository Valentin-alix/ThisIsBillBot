from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.enum_builders import enum_entry
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import (
    enum_field,
    msg_typed_field,
    scalar_field,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import message_signature
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.shapes import (
    BOOLEAN_SHAPE,
    NUMBER_SHAPE,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import (
    access_atom,
    access_message_signature,
    builder_function_access_signature,
    builder_structure_similarity_context,
    declared_field_signature,
    field_access_signature,
)

from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from proto_mapper_assembly.scoring.message_scoring import (
    compute_message_similarity,
    compute_structure_score,
)
from proto_mapper_assembly.scoring.signature_scoring import (
    _access_atom_similarity_from_keys,
    access_atom_sequence_similarity,
    field_evidence_similarity,
    field_signature_similarity,
    function_similarity_from_keys,
)


class TestFieldEvidenceSimilarity:
    def test_untraced_side_scores_neutral_instead_of_zero(self) -> None:
        traced = field_access_signature(accesses=[access_atom(field_offset=24)])
        untraced = field_access_signature(field_offset=32, accesses=[], is_traced=False)

        assert field_signature_similarity(traced, untraced) == 0.0
        assert 0.5 < field_evidence_similarity(traced, untraced) < 1.0

    def test_both_untraced_still_agree(self) -> None:
        left = field_access_signature(accesses=[], is_traced=False)
        right = field_access_signature(field_offset=32, accesses=[], is_traced=False)

        assert field_evidence_similarity(left, right) == 1.0

    def test_untraced_against_traced_without_atom_still_agrees(self) -> None:
        traced_without_atom = field_access_signature(accesses=[])
        untraced = field_access_signature(field_offset=32, accesses=[], is_traced=False)

        assert field_evidence_similarity(traced_without_atom, untraced) == 1.0

    def test_incompatible_shapes_stay_at_zero(self) -> None:
        traced = field_access_signature(field_type_shape=NUMBER_SHAPE)
        untraced = field_access_signature(field_type_shape=BOOLEAN_SHAPE, is_traced=False)

        assert field_evidence_similarity(traced, untraced) == 0

    def test_two_traced_sides_keep_the_atom_comparison(self) -> None:
        left = field_access_signature(accesses=[access_atom(field_offset=24)])
        right = field_access_signature(field_offset=32, accesses=[access_atom(field_offset=32)])

        assert field_evidence_similarity(left, right) == field_signature_similarity(left, right)


class TestAssemblyAccessSimilarity:
    def test_field_signature_similarity_is_symmetric(self) -> None:
        left = field_access_signature(
            field_offset=24,
            accesses=[access_atom(field_offset=24)],
        )
        right = field_access_signature(
            field_offset=32,
            accesses=[access_atom(field_offset=32)],
        )

        assert field_signature_similarity(left, right) == field_signature_similarity(right, left)

    def test_function_similarity_is_symmetric(self) -> None:
        left = builder_function_access_signature(
            self_accesses=[access_atom(field_offset=24)],
            foreign_access_summary=["field:read"],
        )
        right = builder_function_access_signature(
            self_accesses=[access_atom(field_offset=32)],
            foreign_access_summary=["field:read"],
        )

        assert function_similarity_from_keys(
            left.similarity_key,
            right.similarity_key,
        ) == function_similarity_from_keys(
            right.similarity_key,
            left.similarity_key,
        )

    def test_access_atom_similarity_separates_accesses_by_instruction_rank(self) -> None:
        """
        Load-bearing, and measured: flattening this to 1.0 costs mappings.

        The rank is build-unstable and still earns its place, because it is what keeps otherwise
        identical accesses apart. See the note on ``access_atom_similarity_from_keys``.
        """
        left_first = access_atom(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            field_access_index=0,
        )
        right_same_first = access_atom(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            field_access_index=0,
        )
        right_same_second = access_atom(
            field_offset=28,
            field_type_shape=NUMBER_SHAPE,
            field_access_index=1,
        )

        assert _access_atom_similarity_from_keys(
            left_first.similarity_key,
            right_same_first.similarity_key,
        ) > _access_atom_similarity_from_keys(
            left_first.similarity_key,
            right_same_second.similarity_key,
        )

    def test_access_atom_similarity_normalizes_index_delta_by_larger_index(self) -> None:
        left_access = access_atom(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            field_access_index=10,
        )
        right_access = access_atom(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            field_access_index=20,
        )

        assert (
            _access_atom_similarity_from_keys(
                left_access.similarity_key,
                right_access.similarity_key,
            )
            == 0.5
        )

    def test_access_atom_sequence_similarity_compares_accesses_by_order(self) -> None:
        left_first = access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=0)
        left_second = access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=100)
        right_first = access_atom(field_offset=32, field_type_shape=NUMBER_SHAPE, field_access_index=100)
        right_second = access_atom(field_offset=32, field_type_shape=NUMBER_SHAPE, field_access_index=0)

        assert (
            access_atom_sequence_similarity(
                (left_first.similarity_key, left_second.similarity_key),
                (right_first.similarity_key, right_second.similarity_key),
            )
            == 0.0
        )

    def test_field_signature_similarity_tolerates_offset_drift_when_access_shape_matches(self) -> None:
        left = field_access_signature(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            accesses=[access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE)],
        )
        right = field_access_signature(
            field_offset=160,
            field_type_shape=NUMBER_SHAPE,
            accesses=[access_atom(field_offset=160, field_type_shape=NUMBER_SHAPE)],
        )

        assert field_signature_similarity(left, right) > 0.7

    def test_field_signature_similarity_ignores_duplicate_alias_accesses(self) -> None:
        left = field_access_signature(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            accesses=[
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=3),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=3),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=3),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=72),
            ],
        )
        right = field_access_signature(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            accesses=[
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=3),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=72),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=72),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=72),
            ],
        )

        assert field_signature_similarity(left, right) == 1.0

    def test_field_signature_similarity_still_penalizes_unique_access_differences(self) -> None:
        left = field_access_signature(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            accesses=[
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=3),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=72),
            ],
        )
        right = field_access_signature(
            field_offset=24,
            field_type_shape=NUMBER_SHAPE,
            accesses=[
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=3),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=72),
                access_atom(field_offset=24, field_type_shape=NUMBER_SHAPE, field_access_index=100),
            ],
        )

        assert field_signature_similarity(left, right) < 1.0

    def test_structure_similarity_uses_observed_declared_fields(self) -> None:
        live_number = declared_field_signature(field_type_shape=NUMBER_SHAPE)
        live_boolean = declared_field_signature(field_type_shape=BOOLEAN_SHAPE)
        left = access_message_signature(
            declared_field_signatures={FieldKey(24, "map_id_"): live_number},
        )
        one_live_field = access_message_signature(
            message_cls="OtherOne",
            declared_field_signatures={FieldKey(24, "map_id_"): live_number},
        )
        two_live_fields = access_message_signature(
            message_cls="OtherTwo",
            declared_field_signatures={
                FieldKey(24, "map_id_"): live_number,
                FieldKey(32, "instantiate_map_id_"): live_boolean,
            },
        )

        assert compute_structure_score(left, one_live_field) > compute_structure_score(
            left,
            two_live_fields,
        )

    def test_structure_similarity_handles_empty_observed_messages(self) -> None:
        empty_left = access_message_signature(
            declared_field_signatures=[],
        )
        empty_right = access_message_signature(
            message_cls="Other",
            declared_field_signatures=[],
        )
        live_number = declared_field_signature(field_type_shape=NUMBER_SHAPE)
        non_empty_right = access_message_signature(
            message_cls="NonEmpty",
            declared_field_signatures=[live_number],
        )

        assert compute_structure_score(empty_left, empty_right) == 1.0
        assert compute_structure_score(empty_left, non_empty_right) == 0.0

    def test_contextual_structure_similarity_uses_repeated_child_message_structure(self) -> None:
        left_parent, left_parent_signature, left_child_signature = _parent_with_repeated_child_signature(
            parent_name="LeftParent",
            child_name="LeftChild",
            child_fields=[
                scalar_field("first_", 0x20),
                scalar_field("second_", 0x28),
            ],
        )
        right_parent, right_parent_signature, right_child_signature = _parent_with_repeated_child_signature(
            parent_name="RightParent",
            child_name="RightChild",
            child_fields=[scalar_field("first_", 0x20)],
        )
        context = builder_structure_similarity_context(
            left_signatures=[left_parent_signature, left_child_signature],
            right_signatures=[right_parent_signature, right_child_signature],
        )

        assert compute_structure_score(left_parent_signature, right_parent_signature) == 1.0
        assert (
            compute_structure_score(
                left_parent_signature,
                right_parent_signature,
                context=context,
            )
            < 1.0
        )
        assert left_parent.fields[0].normalized_type == "RepeatedField<LeftChild>"
        assert right_parent.fields[0].normalized_type == "RepeatedField<RightChild>"

    def test_contextual_structure_similarity_preserves_matching_child_structure_score(self) -> None:
        _, left_parent_signature, left_child_signature = _parent_with_repeated_child_signature(
            parent_name="LeftParent",
            child_name="LeftChild",
            child_fields=[
                scalar_field("first_", 0x20),
                scalar_field("second_", 0x28),
            ],
        )
        _, right_parent_signature, right_child_signature = _parent_with_repeated_child_signature(
            parent_name="RightParent",
            child_name="RightChild",
            child_fields=[
                scalar_field("first_", 0x20),
                scalar_field("second_", 0x28),
            ],
        )
        context = builder_structure_similarity_context(
            left_signatures=[left_parent_signature, left_child_signature],
            right_signatures=[right_parent_signature, right_child_signature],
        )

        assert (
            compute_structure_score(
                left_parent_signature,
                right_parent_signature,
                context=context,
            )
            == 1.0
        )

    def test_contextual_structure_similarity_uses_enum_signatures_when_available(self) -> None:
        left_field = enum_field(
            field_name="outcome_",
            property_name="Outcome",
            offset=0x10,
            enum_type="LeftOutcome",
        )
        right_field = enum_field(
            field_name="outcome_",
            property_name="Outcome",
            offset=0x10,
            enum_type="RightOutcome",
        )
        left_message = DumpCSMessage(file_descriptor="FD", name="LeftMessage", fields=[left_field])
        right_message = DumpCSMessage(file_descriptor="FD", name="RightMessage", fields=[right_field])
        left_signature = message_signature(
            "LeftMessage",
            declared_field_signatures=[],
            dump_cs_msg=left_message,
            live_field_keys=frozenset(field.field_key for field in left_message.fields),
        )
        right_signature = message_signature(
            "RightMessage",
            declared_field_signatures=[],
            dump_cs_msg=right_message,
            live_field_keys=frozenset(field.field_key for field in right_message.fields),
        )
        context = builder_structure_similarity_context(
            left_signatures=[left_signature],
            right_signatures=[right_signature],
            left_enum_signatures_by_name={"LeftOutcome": enum_entry([1], [2])},
            right_enum_signatures_by_name={"RightOutcome": enum_entry()},
        )

        assert compute_structure_score(left_signature, right_signature) == 1.0
        assert compute_structure_score(left_signature, right_signature, context=context) < 1.0

    def test_message_similarity_blends_structure_and_assembly(self) -> None:
        declared = declared_field_signature(field_type_shape=NUMBER_SHAPE)
        left = access_message_signature(declared_field_signatures=[declared])
        right = access_message_signature(message_cls="Other", declared_field_signatures=[declared])

        score_data = compute_message_similarity(
            left, right, structure_score=compute_structure_score(left, right)
        )

        assert 0.0 < score_data.static_similarity <= 1.0


def _parent_with_repeated_child_signature(
    *,
    parent_name: str,
    child_name: str,
    child_fields: list[DumpCSMessageField],
) -> tuple[DumpCSMessage, MessageAccessSignature, MessageAccessSignature]:
    parent_field = msg_typed_field(
        field_name="children_",
        property_name="Children",
        offset=0x10,
        clr_type=f"RepeatedField<{child_name}>",
        category=FieldCategoryEnum.REPEATED,
    )
    parent_message = DumpCSMessage(file_descriptor="FD", name=parent_name, fields=[parent_field])
    child_message = DumpCSMessage(file_descriptor="FD", name=child_name, fields=child_fields)
    parent_signature = message_signature(
        parent_message.composed_name,
        declared_field_signatures=[],
        dump_cs_msg=parent_message,
        live_field_keys=frozenset(field.field_key for field in parent_message.fields),
    )
    child_signature = message_signature(
        child_message.composed_name,
        declared_field_signatures=[],
        dump_cs_msg=child_message,
        live_field_keys=frozenset(field.field_key for field in child_message.fields),
    )
    return parent_message, parent_signature, child_signature
