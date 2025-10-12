from typing import Any

import numpy as np
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.matching_builders import simple_workspace

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument
from DBDofusUnity.proto_mapper_assembly.affinities.callee_affinity import build_callee_affinity
from DBDofusUnity.proto_mapper_assembly.interfaces.affinity import AffinityResult, AffinitySignalInputs
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace

_OBF_CLASSES = ("obf_achievement", "obf_chat", "obf_silent")
_NON_OBF_CLASSES = ("AchievementEvent", "ChatEvent", "SilentEvent")

_COMMON = "mscorlib.dll/System/String::IsNullOrEmpty/1"
_ACHIEVEMENT = "Ankama.Dofus.Core.DataCenter.dll/Core/DataCenter/DataCenterModule::get_achievements/0"
_CHAT = "Core.Localization.dll/Core/Localization/LocalizedStringUtilities::GetLocalized/2"


def _access_trace(callees_by_function: dict[str, tuple[list[str], list[str]]]) -> AccessTraceDocument:
    """Build a trace where each function touches some classes and calls some methods."""
    functions_by_address: dict[str, Any] = {}
    for function_address, (touched_classes, stable_callees) in callees_by_function.items():
        functions_by_address[function_address] = {
            "start_address": int(function_address, 16),
            "end_address": int(function_address, 16) + 1,
            "size": 1,
            "access_infos": [
                {
                    "type": "typeinfo",
                    "access_kind": "load",
                    "cls": touched_class,
                    "index_in_function": index,
                    "instruction_address": int(function_address, 16) + index,
                    "target_address": index,
                }
                for index, touched_class in enumerate(touched_classes)
            ],
            "opcode_histogram": {},
            "aliases": [],
            "stable_callees": stable_callees,
            "cfg_stats": {
                "basic_block_count": 1,
                "edge_count": 0,
                "back_edge_count": 0,
                "max_block_depth": 1,
            },
        }
    return AccessTraceDocument.model_validate({"functions_by_address": functions_by_address})


def _callee_affinity(
    *,
    workspace: MatchingWorkspace,
    obf_access_trace: AccessTraceDocument,
    non_obf_access_trace: AccessTraceDocument,
) -> AffinityResult:
    """The affinity comes from the traces alone, so the shared base matrix goes in unread."""
    return build_callee_affinity(
        AffinitySignalInputs(
            workspace=workspace,
            base_scores_matrix=np.zeros((len(workspace.non_obf_signatures), len(workspace.obf_signatures))),
            obf_access_trace=obf_access_trace,
            non_obf_access_trace=non_obf_access_trace,
        )
    )


class TestBuildCalleeAffinity:
    def test_rare_shared_callee_separates_otherwise_identical_messages(self) -> None:
        """The point of the signal: two messages with nothing else to tell them apart."""
        workspace = simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES)
        obf_trace = _access_trace(
            {
                "0x1": (["obf_achievement"], [_ACHIEVEMENT, _COMMON]),
                "0x2": (["obf_chat"], [_CHAT, _COMMON]),
            }
        )
        non_obf_trace = _access_trace(
            {
                "0x11": (["AchievementEvent"], [_ACHIEVEMENT, _COMMON]),
                "0x12": (["ChatEvent"], [_CHAT, _COMMON]),
            }
        )

        affinity, mask = _callee_affinity(
            workspace=workspace,
            obf_access_trace=obf_trace,
            non_obf_access_trace=non_obf_trace,
        )

        achievement_row = _NON_OBF_CLASSES.index("AchievementEvent")
        assert mask[achievement_row, _OBF_CLASSES.index("obf_achievement")]
        assert (
            affinity[achievement_row, _OBF_CLASSES.index("obf_achievement")]
            > affinity[achievement_row, _OBF_CLASSES.index("obf_chat")]
        )

    def test_ubiquitous_callee_alone_does_not_separate(self) -> None:
        """A callee every message makes carries no information, whatever its raw overlap."""
        workspace = simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES)
        everywhere = {
            "0x1": (["obf_achievement"], [_COMMON]),
            "0x2": (["obf_chat"], [_COMMON]),
            "0x3": (["obf_silent"], [_COMMON]),
        }
        mirrored = {
            "0x11": (["AchievementEvent"], [_COMMON]),
            "0x12": (["ChatEvent"], [_COMMON]),
            "0x13": (["SilentEvent"], [_COMMON]),
        }

        affinity, _mask = _callee_affinity(
            workspace=workspace,
            obf_access_trace=_access_trace(everywhere),
            non_obf_access_trace=_access_trace(mirrored),
        )

        achievement_row = _NON_OBF_CLASSES.index("AchievementEvent")
        assert np.allclose(affinity[achievement_row], affinity[achievement_row][0])

    def test_message_calling_nothing_recognisable_is_left_out_of_the_mask(self) -> None:
        """Silence is not evidence: the caller must leave those scores untouched."""
        workspace = simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES)
        obf_trace = _access_trace({"0x1": (["obf_achievement"], [_ACHIEVEMENT])})
        non_obf_trace = _access_trace({"0x11": (["AchievementEvent"], [_ACHIEVEMENT])})

        _affinity, mask = _callee_affinity(
            workspace=workspace,
            obf_access_trace=obf_trace,
            non_obf_access_trace=non_obf_trace,
        )

        assert not mask[_NON_OBF_CLASSES.index("SilentEvent")].any()
        assert not mask[:, _OBF_CLASSES.index("obf_silent")].any()

    def test_callees_seen_on_only_one_build_are_ignored(self) -> None:
        """A callee absent from the other side can never match, and would only skew the norms."""
        workspace = simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES)
        obf_trace = _access_trace({"0x1": (["obf_achievement"], ["only.dll/Only::Here/0"])})
        non_obf_trace = _access_trace({"0x11": (["AchievementEvent"], [_ACHIEVEMENT])})

        affinity, mask = _callee_affinity(
            workspace=workspace,
            obf_access_trace=obf_trace,
            non_obf_access_trace=non_obf_trace,
        )

        assert not mask.any()
        assert np.allclose(affinity, 0.0)

    def test_affinity_is_symmetric_under_swapping_the_two_builds(self) -> None:
        """Weighting by one side's frequencies would make the score depend on match direction."""
        workspace = simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES)
        swapped_workspace = simple_workspace(obf_classes=_NON_OBF_CLASSES, non_obf_classes=_OBF_CLASSES)
        obf_trace = _access_trace(
            {"0x1": (["obf_achievement"], [_ACHIEVEMENT, _COMMON]), "0x2": (["obf_chat"], [_CHAT])}
        )
        non_obf_trace = _access_trace(
            {
                "0x11": (["AchievementEvent"], [_ACHIEVEMENT, _COMMON]),
                "0x12": (["ChatEvent"], [_CHAT]),
            }
        )

        affinity, _mask = _callee_affinity(
            workspace=workspace,
            obf_access_trace=obf_trace,
            non_obf_access_trace=non_obf_trace,
        )
        swapped_affinity, _swapped_mask = _callee_affinity(
            workspace=swapped_workspace,
            obf_access_trace=non_obf_trace,
            non_obf_access_trace=obf_trace,
        )

        assert np.allclose(affinity, swapped_affinity.T)
