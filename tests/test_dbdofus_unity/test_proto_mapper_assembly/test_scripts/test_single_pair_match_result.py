from __future__ import annotations

import sys
from typing import cast
from unittest.mock import patch

import pytest
from tests.fixtures.proto_mapper.message_builders import message_signature
from tests.fixtures.proto_mapper.script_builders import (
    field_mapping_result,
    single_pair_matching_inputs,
    single_pair_workspace,
    static_score,
)

import DBDofusUnity.proto_mapper_assembly.scripts.single_pair_match_result as script
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestSinglePairMatchResultScript:
    def test_main_reports_the_requested_pair(self, runtime_data_store: RuntimeDataStore) -> None:
        obf_message = DumpCSMessage(file_descriptor="fd", name="obf")
        non_obf_message = DumpCSMessage(file_descriptor="fd", name="non")
        obf_signature = message_signature("obf", declared_field_signatures=[], dump_cs_msg=obf_message)
        non_obf_signature = message_signature("non", declared_field_signatures=[], dump_cs_msg=non_obf_message)
        reported: list[dict[str, object]] = []

        def capture_report(value: object) -> dict[str, object]:
            assert isinstance(value, dict)
            report = cast("dict[str, object]", value)
            reported.append(report)
            return report

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
            patch.object(
                script,
                "build_matching_workspace",
                return_value=single_pair_workspace(obf_signature=obf_signature, non_obf_signature=non_obf_signature),
            ),
            patch.object(script, "build_message_pair_static_score", return_value=static_score()),
            patch.object(script, "build_field_mapping", return_value=field_mapping_result()),
            patch.object(script, "RuntimeDataStore", return_value=runtime_data_store),
            patch.object(script, "_debug_runtime_remapping"),
            patch.object(sys, "argv", ["single_pair_match_result.py", "--obf", "obf", "--non-obf", "non"]),
            patch.object(script, "ic", side_effect=capture_report),
        ):
            script.main()

        assert len(reported) == 1
        report = reported[0]
        assert report["obf_message_cls"] == "obf"
        assert report["non_obf_message_cls"] == "non"
        assert report["field_mapping"] == {}
        assert report["field_mapping_infos"] == {}

    def test_main_rejects_an_unknown_non_obf_message(self) -> None:
        obf_message = DumpCSMessage(file_descriptor="fd", name="obf")
        obf_signature = message_signature("obf", declared_field_signatures=[], dump_cs_msg=obf_message)

        with (
            patch.object(
                script,
                "load_matching_inputs",
                return_value=single_pair_matching_inputs(obf_message=obf_message, obf_signature=obf_signature),
            ),
            patch.object(
                sys,
                "argv",
                ["single_pair_match_result.py", "--obf", "obf", "--non-obf", "Com.Ankama.TargetMessage"],
            ),
            pytest.raises(ValueError, match=r"Unknown non-obf message alias: 'Com.Ankama.TargetMessage'"),
        ):
            script.main()
