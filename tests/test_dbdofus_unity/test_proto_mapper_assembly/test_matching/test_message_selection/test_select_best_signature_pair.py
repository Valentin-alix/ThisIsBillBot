import numpy as np
import pytest
from tests.fixtures.proto_mapper.matching_builders import (
    nested_signature,
    root_signature,
    select_best_for_test,
    simple_signature,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature


class TestSelectBestSignaturePair:
    @pytest.mark.parametrize(
        ("scores_matrix", "expected_obf_cls"),
        [
            (np.zeros((1, 2)), None),
            (np.array([[0.3, 0.8]]), "obf_b"),
        ],
    )
    def test_selects_best_positive_score(
        self,
        scores_matrix: np.ndarray,
        expected_obf_cls: str | None,
    ) -> None:
        result = select_best_for_test(
            obf_signatures=[simple_signature("obf_a"), simple_signature("obf_b")],
            non_obf_signatures=[simple_signature("clear_a")],
            scores_matrix=scores_matrix,
            roots_only=False,
        )

        if expected_obf_cls is None:
            assert result is None
        else:
            assert result is not None
            assert result.obf_signature.message_cls == expected_obf_cls
            assert result.score == 0.8

    @pytest.mark.parametrize(
        (
            "obf_signatures",
            "non_obf_signatures",
            "scores_matrix",
            "expected_pair",
        ),
        [
            (
                [simple_signature("obf_a")],
                [
                    nested_signature("Parent.Nested", parent_name="Parent", name="Nested"),
                    root_signature("Root"),
                ],
                np.array([[0.9], [0.5]]),
                ("Root", "obf_a"),
            ),
            (
                [
                    nested_signature("Outer.Inner", parent_name="Outer", name="Inner"),
                    root_signature("Outer"),
                ],
                [simple_signature("ClearRoot")],
                np.array([[0.9, 0.5]]),
                ("ClearRoot", "Outer"),
            ),
            (
                [
                    nested_signature(
                        "OtherParent.Inner",
                        parent_name="OtherParent",
                        name="Inner",
                    )
                ],
                [nested_signature("Parent.Nested", parent_name="Parent", name="Nested")],
                np.array([[0.9]]),
                None,
            ),
        ],
    )
    def test_roots_only_filters_nested_messages(
        self,
        obf_signatures: list[MessageAccessSignature],
        non_obf_signatures: list[MessageAccessSignature],
        scores_matrix: np.ndarray,
        expected_pair: tuple[str, str] | None,
    ) -> None:
        result = select_best_for_test(
            obf_signatures=obf_signatures,
            non_obf_signatures=non_obf_signatures,
            scores_matrix=scores_matrix,
            roots_only=True,
        )

        if expected_pair is None:
            assert result is None
        else:
            assert result is not None
            assert (
                result.non_obf_signature.message_cls,
                result.obf_signature.message_cls,
            ) == expected_pair
