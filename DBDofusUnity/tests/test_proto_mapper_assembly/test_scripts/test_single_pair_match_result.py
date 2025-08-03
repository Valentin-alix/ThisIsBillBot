from __future__ import annotations

import sys
from typing import cast
from unittest.mock import patch

import pytest
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.message_builders import (
    field_signature,
    message_signature,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    field_mapping_result,
    single_pair_matching_inputs,
    single_pair_workspace,
    static_score,
)

import proto_mapper_assembly.scripts.single_pair_match_result as script
from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.field_mapping import FieldMappingContext, FieldMappingResult
from proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from proto_mapper_assembly.interfaces.signature_overrides import (
    SignatureOverrideEntry,
)
from proto_mapper_assembly.matching import score_lookup
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from proto_mapper_assembly.scoring.message_scoring import MessageSimilarityScoreData


class TestSinglePairMatchResultScript:
    def test_main_passes_lazy_score_lookup_into_field_mapping(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_message = DumpCSMessage(file_descriptor="fd", name="obf")
        non_obf_message = DumpCSMessage(file_descriptor="fd", name="non")
        obf_signature = message_signature("obf", declared_field_signatures=[], dump_cs_msg=obf_message)
        non_obf_signature = message_signature(
            "non",
            declared_field_signatures=[],
            dump_cs_msg=non_obf_message,
        )

        fake_workspace = single_pair_workspace(
            obf_signature=obf_signature,
            non_obf_signature=non_obf_signature,
        )
        fake_runtime_store = runtime_data_store

        captured_context: list[FieldMappingContext] = []
        captured_result: list[dict[str, object]] = []
        script_score_calls: list[tuple[str, str]] = []
        lookup_score_calls: list[tuple[str, str]] = []

        def fake_build_field_mapping(
            *,
            field_mapping_context: FieldMappingContext,
            **_kwargs: object,
        ) -> FieldMappingResult:
            captured_context.append(field_mapping_context)
            score_by_pair = field_mapping_context.score_by_pair
            assert score_by_pair is not None
            assert score_by_pair[MatchPairKey("obf", "non")] == 0.42
            assert score_by_pair[MatchPairKey("obf", "non")] == 0.42
            return field_mapping_result(
                field_mapping={"fhcu": "interactive_elements"},
                field_mapping_infos={"fhcu": {"interactive_elements": 0.7531628598484849}},
            )

        def fake_script_score(
            left: MessageAccessSignature,
            right: MessageAccessSignature,
            *,
            structure_context: object | None = None,
        ) -> MessageSimilarityScoreData:
            assert structure_context is not None
            script_score_calls.append((left.message_cls, right.message_cls))
            return static_score()

        def fake_lookup_score(
            left: MessageAccessSignature,
            right: MessageAccessSignature,
            *,
            structure_context: object | None = None,
        ) -> MessageSimilarityScoreData:
            assert structure_context is not None
            lookup_score_calls.append((left.message_cls, right.message_cls))
            return static_score(
                function_similarity=0.49333333333333335,
                fields_similarity=0.49333333333333335,
            )

        def fake_ic(result: object) -> dict[str, object]:
            assert isinstance(result, dict)
            result_dict = cast("dict[str, object]", result)
            captured_result.append(result_dict)
            return result_dict

        with (
            patch.object(
                script,
                "load_matching_inputs",
                return_value=single_pair_matching_inputs(
                    obf_message=obf_message,
                    non_obf_message=non_obf_message,
                    obf_signature=obf_signature,
                    non_obf_signature=non_obf_signature,
                ),
            ),
            patch.object(script, "build_matching_workspace", return_value=fake_workspace),
            patch.object(script, "build_message_pair_static_score", side_effect=fake_script_score),
            patch.object(
                score_lookup,
                "build_message_pair_static_score",
                side_effect=fake_lookup_score,
            ),
            patch.object(script, "build_field_mapping", side_effect=fake_build_field_mapping),
            patch.object(script, "RuntimeDataStore", return_value=fake_runtime_store),
            patch.object(sys, "argv", ["single_pair_match_result.py", "--obf", "obf", "--non-obf", "non"]),
            patch.object(script, "ic", side_effect=fake_ic),
        ):
            script.main()

        assert len(captured_context) == 1
        field_mapping_context = captured_context[0]
        assert field_mapping_context.score_by_pair is not None
        assert field_mapping_context.score_by_pair[MatchPairKey("obf", "non")] == 0.42
        assert field_mapping_context.runtime_data_store is fake_runtime_store
        assert script_score_calls == [("obf", "non")]
        assert lookup_score_calls == [("obf", "non")]
        assert len(captured_result) == 1
        result = captured_result[0]
        assert result["obf_message_cls"] == "obf"
        assert result["non_obf_message_cls"] == "non"
        assert result["access_score"] == "function sim 0.3 | field sim 0.3"
        assert result["structure_score"] == 0.2
        assert result["field_mapping"] == {"fhcu": "interactive_elements"}
        assert result["field_mapping_infos"] == {"fhcu": {"interactive_elements": 0.7531628598484849}}
        assert result["total_score"] == 0.27499999999999997

    def test_main_applies_stored_non_obf_signature_overrides(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_message = DumpCSMessage(file_descriptor="fd", name="obf")
        non_obf_message = DumpCSMessage(file_descriptor="fd", name="non")
        obf_signature = message_signature("obf", declared_field_signatures=[], dump_cs_msg=obf_message)
        base_non_obf_signature = message_signature(
            "non",
            declared_field_signatures=[],
            dump_cs_msg=non_obf_message,
        )
        _override_field_sig = field_signature(64, None)
        override_field_signatures = [_override_field_sig]
        override = SignatureOverrideEntry(
            function_signatures=list(base_non_obf_signature.function_signatures),
            field_signatures={"field": _override_field_sig},
        )

        fake_workspace = single_pair_workspace(
            obf_signature=obf_signature,
            non_obf_signature=base_non_obf_signature,
        )

        with (
            patch.object(
                script,
                "load_matching_inputs",
                return_value=single_pair_matching_inputs(
                    obf_message=obf_message,
                    non_obf_message=non_obf_message,
                    obf_signature=obf_signature,
                    non_obf_signatures_by_cls={
                        "non": base_non_obf_signature.model_copy(
                            update={"field_signatures": list(override.field_signatures.values())}
                        )
                    },
                ),
            ),
            patch.object(script, "build_matching_workspace", return_value=fake_workspace),
            patch.object(
                script,
                "build_message_pair_static_score",
                return_value=static_score(),
            ),
            patch.object(
                script,
                "build_field_mapping",
                return_value=field_mapping_result(),
            ) as build_field_mapping_mock,
            patch.object(script, "RuntimeDataStore", return_value=runtime_data_store),
            patch.object(script, "_debug_runtime_remapping"),
            patch.object(sys, "argv", ["single_pair_match_result.py", "--obf", "obf", "--non-obf", "non"]),
            patch.object(script, "ic"),
        ):
            script.main()

        field_mapping_context = build_field_mapping_mock.call_args.kwargs["field_mapping_context"]
        assert isinstance(field_mapping_context, FieldMappingContext)
        assert field_mapping_context.score_by_pair is not None
        overridden_non_obf_signature = build_field_mapping_mock.call_args.kwargs["non_obf_signature"]
        assert isinstance(overridden_non_obf_signature, MessageAccessSignature)
        assert overridden_non_obf_signature.field_signatures == override_field_signatures

    def test_main_accepts_non_obf_class_added_by_pipeline_injection(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_message = DumpCSMessage(file_descriptor="fd_obf", name="obf")
        existing_non_obf_message = DumpCSMessage(
            file_descriptor="fd_non",
            name="ExistingMessage",
            namespace="Com.Ankama",
        )
        injected_non_obf_message = DumpCSMessage(
            file_descriptor="fd_non",
            name="TargetMessage",
            namespace="Com.Ankama",
        )
        obf_signature = message_signature("obf", declared_field_signatures=[], dump_cs_msg=obf_message)
        injected_non_obf_signature = message_signature(
            "Com.Ankama.TargetMessage",
            declared_field_signatures=[],
            dump_cs_msg=injected_non_obf_message,
        )

        fake_workspace = single_pair_workspace(
            obf_signature=obf_signature,
            non_obf_signature=injected_non_obf_signature,
        )

        with (
            patch.object(
                script,
                "load_matching_inputs",
                return_value=single_pair_matching_inputs(
                    obf_message=obf_message,
                    obf_signature=obf_signature,
                    non_obf_messages_by_cls={
                        "Com.Ankama.ExistingMessage": existing_non_obf_message,
                        "Com.Ankama.TargetMessage": injected_non_obf_message,
                    },
                    non_obf_signatures_by_cls={"Com.Ankama.TargetMessage": injected_non_obf_signature},
                ),
            ),
            patch.object(script, "build_matching_workspace", return_value=fake_workspace),
            patch.object(
                script,
                "build_message_pair_static_score",
                return_value=static_score(),
            ),
            patch.object(
                script,
                "build_field_mapping",
                return_value=field_mapping_result(),
            ),
            patch.object(script, "RuntimeDataStore", return_value=runtime_data_store),
            patch.object(script, "_debug_runtime_remapping"),
            patch.object(
                sys,
                "argv",
                [
                    "single_pair_match_result.py",
                    "--obf",
                    "obf",
                    "--non-obf",
                    "Com.Ankama.TargetMessage",
                ],
            ),
            patch.object(script, "ic"),
        ):
            script.main()

    def test_main_raises_when_non_obf_class_remains_missing_after_override_processing(self) -> None:
        obf_message = DumpCSMessage(file_descriptor="fd", name="obf")
        obf_signature = message_signature("obf", declared_field_signatures=[], dump_cs_msg=obf_message)

        with (
            patch.object(
                script,
                "load_matching_inputs",
                return_value=single_pair_matching_inputs(
                    obf_message=obf_message,
                    obf_signature=obf_signature,
                ),
            ),
            patch.object(
                sys,
                "argv",
                [
                    "single_pair_match_result.py",
                    "--obf",
                    "obf",
                    "--non-obf",
                    "Com.Ankama.TargetMessage",
                ],
            ),
            pytest.raises(ValueError, match=r"Unknown non-obf message alias: 'Com.Ankama.TargetMessage'"),
        ):
            script.main()

    def test_main_accepts_override_only_non_obf_class(self, runtime_data_store: RuntimeDataStore) -> None:
        obf_message = DumpCSMessage(file_descriptor="fd_obf", name="irk")
        override_only_message = DumpCSMessage(
            file_descriptor="fd_non",
            name="MapMovementConfirmResponse",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Gamemap",
        )
        obf_signature = message_signature("irk", declared_field_signatures=[], dump_cs_msg=obf_message)
        override_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Gamemap.MapMovementConfirmResponse",
            declared_field_signatures=[],
            dump_cs_msg=override_only_message,
        )

        fake_workspace = single_pair_workspace(
            obf_signature=obf_signature,
            non_obf_signature=override_signature,
        )

        with (
            patch.object(
                script,
                "load_matching_inputs",
                return_value=single_pair_matching_inputs(
                    obf_message=obf_message,
                    non_obf_message=override_only_message,
                    obf_signature=obf_signature,
                    non_obf_signature=override_signature,
                ),
            ),
            patch.object(script, "build_matching_workspace", return_value=fake_workspace),
            patch.object(
                script,
                "build_message_pair_static_score",
                return_value=static_score(structure_similarity=0.0),
            ),
            patch.object(
                script,
                "build_field_mapping",
                return_value=field_mapping_result(),
            ),
            patch.object(script, "RuntimeDataStore", return_value=runtime_data_store),
            patch.object(script, "_debug_runtime_remapping"),
            patch.object(
                sys,
                "argv",
                [
                    "single_pair_match_result.py",
                    "--obf",
                    "irk",
                    "--non-obf",
                    "Com.Ankama.Dofus.Server.Game.Protocol.Gamemap.MapMovementConfirmResponse",
                ],
            ),
            patch.object(script, "ic"),
        ):
            script.main()
