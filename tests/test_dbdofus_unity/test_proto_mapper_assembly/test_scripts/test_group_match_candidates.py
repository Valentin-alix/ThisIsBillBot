from __future__ import annotations

import numpy as np
import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import access_message_signature

from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.matching.workspace import build_matching_workspace
from proto_mapper_assembly.scripts.group_match_candidates import (
    GroupAnalysis,
    GroupClaim,
    ObfGroupState,
    _resolve_non_obf_descriptor,
)


def _analysis(
    *,
    non_obf_signatures: list[MessageAccessSignature],
    obf_signatures: list[MessageAccessSignature],
    obf_cls_by_non_obf_cls: dict[str, str],
    obf_group_states: dict[str, ObfGroupState] | None = None,
) -> GroupAnalysis:
    workspace = build_matching_workspace(
        obf_signatures=obf_signatures,
        non_obf_signatures=non_obf_signatures,
        obf_messages_by_cls={s.message_cls: s.dump_cs_msg for s in obf_signatures},
        non_obf_messages_by_cls={s.message_cls: s.dump_cs_msg for s in non_obf_signatures},
    )
    return GroupAnalysis(
        workspace=workspace,
        scores_matrix=np.zeros((len(non_obf_signatures), len(obf_signatures))),
        group_scores_matrix=np.zeros((len(workspace.non_obf_groups), len(workspace.obf_groups))),
        non_obf_descriptors=workspace.non_obf_group_descriptors,
        obf_descriptors=workspace.obf_group_descriptors,
        obf_group_state_by_descriptor=obf_group_states or {},
        obf_cls_by_non_obf_cls=obf_cls_by_non_obf_cls,
        pinned_obf_classes=frozenset(),
        obf_handler_count_by_cls={},
        non_obf_handler_count_by_cls={},
    )


class TestClaimVerdict:
    """The verdict is the whole point of the report: it says whether a claim is worth contesting."""

    def test_a_claim_backed_by_no_pin_is_unverified(self) -> None:
        state = ObfGroupState(
            obf_descriptor="izp",
            size=21,
            claims=(GroupClaim(non_obf_descriptor="HouseReflection", message_count=18, pinned_count=0),),
        )

        assert state.verdict == "UNVERIFIED"
        assert state.claimed_count == 18
        assert state.pinned_count == 0

    def test_a_claim_backed_by_enough_pins_is_solid(self) -> None:
        state = ObfGroupState(
            obf_descriptor="krk",
            size=8,
            claims=(
                GroupClaim(non_obf_descriptor="ClientVerificationReflection", message_count=6, pinned_count=4),
            ),
        )

        assert state.verdict == "SOLID"

    def test_a_single_pin_is_not_enough_to_call_a_claim_solid(self) -> None:
        state = ObfGroupState(
            obf_descriptor="jap",
            size=26,
            claims=(GroupClaim(non_obf_descriptor="HavenBagReflection", message_count=23, pinned_count=1),),
        )

        assert state.verdict == "weak"

    def test_an_unclaimed_group_reads_as_free(self) -> None:
        state = ObfGroupState(obf_descriptor="jbw", size=4, claims=())

        assert state.describe_claims() == "free"
        assert state.verdict == "UNVERIFIED"

    def test_claims_are_described_with_their_pin_backing(self) -> None:
        state = ObfGroupState(
            obf_descriptor="jap",
            size=26,
            claims=(
                GroupClaim(non_obf_descriptor="HavenBagReflection", message_count=23, pinned_count=1),
                GroupClaim(non_obf_descriptor="BreachReflection", message_count=1, pinned_count=0),
            ),
        )

        assert state.describe_claims() == "HavenBag=23(1 pins), Breach=1(0 pins)"


class TestResolveNonObfDescriptor:
    _DESCRIPTORS = ("BreachReflection", "BreedingReflection", "MountReflection")

    def test_accepts_the_short_form(self) -> None:
        assert _resolve_non_obf_descriptor("Breach", self._DESCRIPTORS) == "BreachReflection"

    def test_accepts_the_full_form_whatever_the_case(self) -> None:
        assert _resolve_non_obf_descriptor("mountREFLECTION", self._DESCRIPTORS) == "MountReflection"

    def test_rejects_an_ambiguous_prefix(self) -> None:
        with pytest.raises(SystemExit, match="Ambiguous descriptor"):
            _resolve_non_obf_descriptor("Bree", ("BreedingReflection", "BreedingPaddockReflection"))

    def test_rejects_an_unknown_descriptor(self) -> None:
        with pytest.raises(SystemExit, match="Unknown non-obf file descriptor"):
            _resolve_non_obf_descriptor("Nope", self._DESCRIPTORS)


class TestCoherence:
    def test_a_file_landing_in_one_group_is_fully_coherent(self) -> None:
        non_obf = [
            access_message_signature(message_cls="Ns.Alpha", file_descriptor="BreachReflection"),
            access_message_signature(message_cls="Ns.Beta", file_descriptor="BreachReflection"),
        ]
        obf = [
            access_message_signature(message_cls="jav", file_descriptor="jap"),
            access_message_signature(message_cls="jau", file_descriptor="jap"),
        ]

        analysis = _analysis(
            non_obf_signatures=non_obf,
            obf_signatures=obf,
            obf_cls_by_non_obf_cls={"Ns.Alpha": "jav", "Ns.Beta": "jau"},
        )

        assert analysis.coherence("BreachReflection") == (1.0, "jap", 2)

    def test_a_file_split_across_groups_scores_its_plurality_share(self) -> None:
        non_obf = [
            access_message_signature(message_cls="Ns.Alpha", file_descriptor="BreachReflection"),
            access_message_signature(message_cls="Ns.Beta", file_descriptor="BreachReflection"),
            access_message_signature(message_cls="Ns.Gamma", file_descriptor="BreachReflection"),
        ]
        obf = [
            access_message_signature(message_cls="jav", file_descriptor="jap"),
            access_message_signature(message_cls="jau", file_descriptor="jap"),
            access_message_signature(message_cls="hou", file_descriptor="hno"),
        ]

        analysis = _analysis(
            non_obf_signatures=non_obf,
            obf_signatures=obf,
            obf_cls_by_non_obf_cls={"Ns.Alpha": "jav", "Ns.Beta": "jau", "Ns.Gamma": "hou"},
        )

        coherence = analysis.coherence("BreachReflection")
        assert coherence is not None
        share, dominant, mapping_count = coherence
        assert dominant == "jap"
        assert mapping_count == 3
        assert share == pytest.approx(2 / 3)

    def test_unmapped_members_do_not_count_towards_the_denominator(self) -> None:
        """The score denominator is the mappings, not the members: 1 of 15 mapped still reads 1.0."""
        non_obf = [
            access_message_signature(message_cls="Ns.Alpha", file_descriptor="PaddockReflection"),
            access_message_signature(message_cls="Ns.Beta", file_descriptor="PaddockReflection"),
        ]
        obf = [access_message_signature(message_cls="hir", file_descriptor="hij")]

        analysis = _analysis(
            non_obf_signatures=non_obf,
            obf_signatures=obf,
            obf_cls_by_non_obf_cls={"Ns.Alpha": "hir"},
        )

        assert analysis.coherence("PaddockReflection") == (1.0, "hij", 1)

    def test_a_file_with_no_mapping_at_all_has_no_coherence(self) -> None:
        non_obf = [access_message_signature(message_cls="Ns.Alpha", file_descriptor="DebugReflection")]
        obf = [access_message_signature(message_cls="krt", file_descriptor="krk")]

        analysis = _analysis(non_obf_signatures=non_obf, obf_signatures=obf, obf_cls_by_non_obf_cls={})

        assert analysis.coherence("DebugReflection") is None
