import pytest

from DBDofusUnity.proto_mapper_assembly.interfaces.function_access_signature import ReturnRole
from DBDofusUnity.proto_mapper_assembly.scoring import enum_similarity, message_scoring, signature_scoring
from DBDofusUnity.proto_mapper_assembly.matching import score_constraints
from DBDofusUnity.proto_mapper_assembly.scripts.benchmark_ablation import ablate_signals
from tests.fixtures.proto_mapper.signatures import builder_function_access_signature


def test_assembly_ablation_renormalizes_and_restores_all_scorers() -> None:
    left = builder_function_access_signature(size=100).similarity_key._replace(opcode_histogram=(("mov", 2),))
    right = left._replace(size=400, opcode_histogram=(("call", 2),), foreign_access_summary=("foreign",))
    original_score = signature_scoring.function_similarity_from_keys(left, right)
    assert original_score < 1.0

    with ablate_signals(frozenset(("opcode_histogram", "foreign_access", "function_size"))):
        for module in (signature_scoring, message_scoring, enum_similarity):
            assert module.function_similarity_from_keys(left, right) == pytest.approx(1.0)
            assert (
                module.function_similarity_from_keys(left, right._replace(return_role=ReturnRole.VOID)) == 0.0
            )

    for module in (signature_scoring, message_scoring, enum_similarity):
        assert module.function_similarity_from_keys(left, right) == original_score


def test_ablation_rejects_unknown_signal() -> None:
    with pytest.raises(ValueError, match="Unknown ablation"):
        with ablate_signals(frozenset(("typo",))):
            pytest.fail("Invalid experiments must not run")


def test_oneof_penalty_ablation_removes_only_partition_factor() -> None:
    original_floor = message_scoring._ONEOF_PARTITION_MISMATCH_FLOOR
    with ablate_signals(frozenset(("oneof_partition_penalty",))):
        assert message_scoring._ONEOF_PARTITION_MISMATCH_FLOOR == 1.0
    assert message_scoring._ONEOF_PARTITION_MISMATCH_FLOOR == original_floor


def test_capture_order_ablation_disables_constraint_hook_and_restores_it() -> None:
    original = score_constraints.apply_capture_sequence_order_scores
    with ablate_signals(frozenset(("capture_sequence_order",))):
        assert score_constraints.apply_capture_sequence_order_scores is not original
    assert score_constraints.apply_capture_sequence_order_scores is original
