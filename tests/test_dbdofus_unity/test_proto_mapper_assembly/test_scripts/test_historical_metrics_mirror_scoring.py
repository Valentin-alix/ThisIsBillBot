import unittest

from tests.fixtures.proto_mapper.shapes import (
    BOOLEAN_SHAPE,
    MESSAGE_SHAPE,
    NUMBER_SHAPE,
    REPEATED_NUMBER_SHAPE,
    STRING_SHAPE,
)
from tests.fixtures.proto_mapper.signatures import (
    access_atom,
    access_message_signature,
    builder_function_access_signature,
    declared_field_signature,
    field_access_signature,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    FieldAccessSignatures,
    MessageAccessSignature,
    ReturnRole,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.function_access_signature import FunctionSimilarityKey
from DBDofusUnity.proto_mapper_assembly.scoring import message_scoring, signature_scoring
from DBDofusUnity.proto_mapper_assembly.scripts.audit_historical_assembly_metrics import (
    _field_access_compatible_position_multiset_similarity,
    _function_access_sequence_indexed_similarity,
    _structure_declared_shape_similarity,
    _structure_oneof_partition_similarity,
)


def _message_signatures() -> list[MessageAccessSignature]:
    return [
        access_message_signature(
            message_cls="Ns.Empty",
            declared_field_signatures=[],
        ),
        access_message_signature(
            message_cls="Ns.Scalars",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(STRING_SHAPE),
            ],
        ),
        access_message_signature(
            message_cls="Ns.ScalarsReordered",
            declared_field_signatures=[
                declared_field_signature(STRING_SHAPE),
                declared_field_signature(NUMBER_SHAPE),
            ],
        ),
        access_message_signature(
            message_cls="Ns.Mixed",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(BOOLEAN_SHAPE),
                declared_field_signature(REPEATED_NUMBER_SHAPE),
            ],
        ),
        access_message_signature(
            message_cls="Ns.OneSmallOneof",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE, is_oneof_member=True),
                declared_field_signature(STRING_SHAPE, is_oneof_member=True),
            ],
        ),
        access_message_signature(
            message_cls="Ns.OneofPlusScalar",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE, is_oneof_member=True),
                declared_field_signature(STRING_SHAPE, is_oneof_member=True),
                declared_field_signature(MESSAGE_SHAPE),
            ],
        ),
    ]


def _field_signatures() -> list[FieldAccessSignatures]:
    return [
        field_access_signature(field_offset=24, field_type_shape=NUMBER_SHAPE, accesses=[]),
        field_access_signature(
            field_offset=32,
            field_type_shape=NUMBER_SHAPE,
            accesses=[access_atom(field_offset=32, field_access_index=0)],
        ),
        field_access_signature(
            field_offset=40,
            field_type_shape=NUMBER_SHAPE,
            accesses=[
                access_atom(field_offset=40, field_access_index=0),
                access_atom(field_offset=40, access_kind="write", field_access_index=1),
            ],
        ),
        field_access_signature(
            field_offset=48,
            field_type_shape=STRING_SHAPE,
            accesses=[access_atom(field_offset=48, field_access_index=0)],
        ),
        field_access_signature(field_offset=56, field_type_shape=MESSAGE_SHAPE, accesses=[], is_traced=False),
    ]


def _function_similarity_keys() -> list[FunctionSimilarityKey]:
    signatures = [
        builder_function_access_signature(self_accesses=[]),
        builder_function_access_signature(self_accesses=[access_atom(field_offset=24)]),
        builder_function_access_signature(
            self_accesses=[
                access_atom(field_offset=24, field_access_index=0),
                access_atom(field_offset=32, field_access_index=1),
            ]
        ),
        builder_function_access_signature(
            return_role=ReturnRole.OTHER,
            takes_message_parameter=False,
            size=90,
            self_accesses=[access_atom(field_offset=32, access_kind="write")],
        ),
    ]
    return [signature.similarity_key for signature in signatures]


class TestMetricsMirrorTheScoringModule(unittest.TestCase):
    def test_declared_shape_metric_matches_the_scoring_module(self) -> None:
        for left in _message_signatures():
            for right in _message_signatures():
                with self.subTest(left=left.message_cls, right=right.message_cls):
                    assert _structure_declared_shape_similarity(
                        left, right
                    ) == message_scoring._declared_shape_similarity(left, right)

    def test_oneof_partition_metric_matches_the_scoring_module(self) -> None:
        for left in _message_signatures():
            for right in _message_signatures():
                with self.subTest(left=left.message_cls, right=right.message_cls):
                    assert _structure_oneof_partition_similarity(
                        left, right
                    ) == message_scoring._oneof_partition_similarity(left, right)

    def test_field_access_compatible_position_metric_matches_the_scoring_module(self) -> None:
        for left in _field_signatures():
            for right in _field_signatures():
                with self.subTest(left=left.field_key, right=right.field_key):
                    assert _field_access_compatible_position_multiset_similarity(
                        left, right
                    ) == signature_scoring.field_signature_similarity(left, right)

    def test_function_access_sequence_metric_matches_the_scoring_module(self) -> None:
        for left in _function_similarity_keys():
            for right in _function_similarity_keys():
                with self.subTest(left=left.self_accesses, right=right.self_accesses):
                    assert _function_access_sequence_indexed_similarity(
                        left, right
                    ) == signature_scoring.access_atom_sequence_similarity(
                        left.self_accesses, right.self_accesses
                    )


if __name__ == "__main__":
    unittest.main()
