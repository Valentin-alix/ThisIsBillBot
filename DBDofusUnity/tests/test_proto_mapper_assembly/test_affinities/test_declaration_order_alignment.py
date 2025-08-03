from typing import Any

import numpy as np
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.matching_builders import simple_workspace

from proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument
from proto_mapper_assembly.affinities.declaration_order_alignment import (
    build_declaration_order_affinity,
)
from proto_mapper_assembly.interfaces.affinity import AffinitySignalInputs

_OBF_CLASSES = ("obf_a1", "obf_a2", "obf_a3")
_NON_OBF_CLASSES = ("ClearA1", "ClearA2", "ClearA3", "ClearUnwrapped")
_TIED_SCORES = np.array(
    [
        [0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5],
        [0.1, 0.1, 0.1],
    ]
)
"""Every wrapped message scores the same against every candidate: only the slot can separate them."""


def _access_trace(message_by_alias: dict[str, str]) -> AccessTraceDocument:
    """Build a trace where each alias is a wrapper method touching exactly one message."""
    functions_by_address: dict[str, Any] = {}
    for index, (alias_name, message_cls) in enumerate(message_by_alias.items()):
        address = 0x1000 + index * 0x10
        functions_by_address[hex(address)] = {
            "start_address": address,
            "end_address": address + 1,
            "size": 1,
            "access_infos": [
                {
                    "type": "field",
                    "access_kind": "read",
                    "cls": message_cls,
                    "field_name": "value_",
                    "property_name": "Value",
                    "field_offset": 0x18,
                    "index_in_function": 0,
                    "instruction_address": address,
                }
            ],
            "opcode_histogram": {},
            "aliases": [
                {
                    "name": alias_name,
                    "parameters": [],
                    "return_type": "Boolean",
                    "group": "Core.dll/wrapper",
                }
            ],
            "stable_callees": [],
            "cfg_stats": None,
        }
    return AccessTraceDocument.model_validate({"functions_by_address": functions_by_address})


def _build_affinity(
    obf_message_by_alias: dict[str, str],
    non_obf_message_by_alias: dict[str, str],
    scores_matrix: np.ndarray = _TIED_SCORES,
) -> tuple[np.ndarray, np.ndarray]:
    return build_declaration_order_affinity(
        AffinitySignalInputs(
            workspace=simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES),
            base_scores_matrix=scores_matrix,
            obf_access_trace=_access_trace(obf_message_by_alias),
            non_obf_access_trace=_access_trace(non_obf_message_by_alias),
        )
    )


_NON_OBF_SEGMENT = {
    "own::Boolean bara(x)": "ClearA1",
    "own::Boolean barb(x)": "ClearA2",
    "own::Boolean barc(x)": "ClearA3",
}


class TestDeclarationOrderAlignment:
    def test_slot_order_pairs_messages_that_scores_cannot_separate(self) -> None:
        affinity_matrix, applicable_mask = _build_affinity(
            {
                "wrp::Boolean zsa(y)": "obf_a1",
                "wrp::Boolean zsb(y)": "obf_a2",
                "wrp::Boolean zsc(y)": "obf_a3",
            },
            _NON_OBF_SEGMENT,
        )

        assert applicable_mask[:3, :].all()
        assert affinity_matrix[0, 0] == 1.0
        assert affinity_matrix[1, 1] == 1.0
        assert affinity_matrix[2, 2] == 1.0

    def test_the_obfuscated_naming_order_drives_the_pairing_not_the_matrix_order(self) -> None:
        # obf_a3 is declared first in the wrapper: it must take the first non-obfuscated slot even
        # though it sits last in the score matrix.
        affinity_matrix, _ = _build_affinity(
            {
                "wrp::Boolean zsa(y)": "obf_a3",
                "wrp::Boolean zsb(y)": "obf_a1",
                "wrp::Boolean zsc(y)": "obf_a2",
            },
            _NON_OBF_SEGMENT,
        )

        assert affinity_matrix[0, 2] == 1.0
        assert affinity_matrix[1, 0] == 1.0
        assert affinity_matrix[2, 1] == 1.0

    def test_landing_on_the_wrong_slot_only_costs_a_little(self) -> None:
        # Two wrappers swapping places between builds happens, so an unaligned pair inside a matched
        # segment must stay clearly above a pair the segment says nothing about.
        affinity_matrix, _ = _build_affinity(
            {
                "wrp::Boolean zsa(y)": "obf_a1",
                "wrp::Boolean zsb(y)": "obf_a2",
                "wrp::Boolean zsc(y)": "obf_a3",
            },
            _NON_OBF_SEGMENT,
        )

        assert 0.0 < affinity_matrix[0, 1] < affinity_matrix[0, 0]

    def test_messages_without_a_wrapper_are_not_constrained(self) -> None:
        _, applicable_mask = _build_affinity(
            {
                "wrp::Boolean zsa(y)": "obf_a1",
                "wrp::Boolean zsb(y)": "obf_a2",
                "wrp::Boolean zsc(y)": "obf_a3",
            },
            _NON_OBF_SEGMENT,
        )

        assert not applicable_mask[3].any()

    def test_readable_class_names_carry_no_order_and_are_ignored(self) -> None:
        # Only the generated wrappers get sequential lowercase names; a class that kept its real name
        # has method names in arbitrary order and must not be read as a declaration segment.
        affinity_matrix, applicable_mask = _build_affinity(
            {
                "Core.Handler::Boolean HandleAlpha(y)": "obf_a1",
                "Core.Handler::Boolean HandleBeta(y)": "obf_a2",
                "Core.Handler::Boolean HandleGamma(y)": "obf_a3",
            },
            _NON_OBF_SEGMENT,
        )

        assert not applicable_mask.any()
        assert not affinity_matrix.any()

    def test_a_segment_shorter_than_the_minimum_is_ignored(self) -> None:
        _, applicable_mask = _build_affinity(
            {"wrp::Boolean zsa(y)": "obf_a1", "wrp::Boolean zsb(y)": "obf_a2"},
            {"own::Boolean bara(x)": "ClearA1", "own::Boolean barb(x)": "ClearA2"},
        )

        assert not applicable_mask.any()

    def test_a_jump_in_the_naming_sequence_splits_the_segment(self) -> None:
        # ``zzz`` is nowhere near ``zsa``/``zsb``: it belongs to another part of the class, so the segment
        # stops before it and drops below the minimum length.
        _, applicable_mask = _build_affinity(
            {
                "wrp::Boolean zsa(y)": "obf_a1",
                "wrp::Boolean zsb(y)": "obf_a2",
                "wrp::Boolean zzz(y)": "obf_a3",
            },
            _NON_OBF_SEGMENT,
        )

        assert not applicable_mask.any()

    def test_empty_traces_constrain_nothing(self) -> None:
        affinity_matrix, applicable_mask = build_declaration_order_affinity(
            AffinitySignalInputs(
                workspace=simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES),
                base_scores_matrix=_TIED_SCORES,
                obf_access_trace=_access_trace({}),
                non_obf_access_trace=_access_trace({}),
            )
        )

        assert affinity_matrix.shape == _TIED_SCORES.shape
        assert not applicable_mask.any()
