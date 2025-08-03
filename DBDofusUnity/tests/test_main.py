from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest
from DBDofusUnity.main import _gen_new_msg

# `_gen_new_msg` imports run_pipeline lazily, so that nothing loads the generated *_pb2
# modules before gen_python rewrites them. Patch it where it is defined, not on main.
_RUN_PIPELINE = "proto_mapper_assembly.pipeline.run_pipeline"


def _build_arguments(**overrides: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "class_name": "Com.Ankama.Dofus.Server.Game.Protocol.Fight.NewMsg",
        "obf_class_name": "koa",
        "field_mappings": [],
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class TestGenObfPythonCommand:
    def test_chains_all_steps(self) -> None:
        arguments = _build_arguments()

        with (
            patch("DBDofusUnity.main.gen_python") as gen_python,
            patch("DBDofusUnity.main.build_new_dump_cs_entries") as build_new_dump_cs_entries,
            patch("DBDofusUnity.main.PINNED_PAIRS_FILE", "pinned_pairs.json"),
            patch("DBDofusUnity.main.upsert_pinned_pair") as upsert_pinned_pair,
            patch("DBDofusUnity.main.upsert_pinned_field_mapping") as upsert_pinned_field_mapping,
            patch("DBDofusUnity.main.run_export_signature_overrides") as run_export_signature_overrides,
            patch(_RUN_PIPELINE) as run_pipeline,
        ):
            _gen_new_msg(arguments)

        gen_python.assert_called_once_with(arguments)
        build_new_dump_cs_entries.assert_called_once_with(
            ["Com.Ankama.Dofus.Server.Game.Protocol.Fight.NewMsg"]
        )
        upsert_pinned_pair.assert_called_once_with(
            "pinned_pairs.json", "koa", "Com.Ankama.Dofus.Server.Game.Protocol.Fight.NewMsg"
        )
        upsert_pinned_field_mapping.assert_not_called()
        run_export_signature_overrides.assert_called_once_with()
        run_pipeline.assert_called_once_with(do_load_pinned_pair=True)

    def test_applies_field_mappings_in_order(self) -> None:
        arguments = _build_arguments(field_mappings=["obf_a=non_obf_a", "obf_b=non_obf_b"])

        with (
            patch("DBDofusUnity.main.gen_python"),
            patch("DBDofusUnity.main.build_new_dump_cs_entries"),
            patch("DBDofusUnity.main.upsert_pinned_pair"),
            patch("DBDofusUnity.main.upsert_pinned_field_mapping") as upsert_pinned_field_mapping,
            patch("DBDofusUnity.main.run_export_signature_overrides"),
            patch(_RUN_PIPELINE),
        ):
            _gen_new_msg(arguments)

        assert upsert_pinned_field_mapping.call_count == 2
        first_call, second_call = upsert_pinned_field_mapping.call_args_list
        assert first_call.args[1:3] == ("koa", "Com.Ankama.Dofus.Server.Game.Protocol.Fight.NewMsg")
        assert first_call.args[3:] == ("obf_a", "non_obf_a")
        assert second_call.args[3:] == ("obf_b", "non_obf_b")

    def test_rejects_field_mapping_without_separator(self) -> None:
        arguments = _build_arguments(field_mappings=["invalid_without_equals"])

        with (
            patch("DBDofusUnity.main.gen_python"),
            patch("DBDofusUnity.main.build_new_dump_cs_entries"),
            patch("DBDofusUnity.main.upsert_pinned_pair"),
            patch("DBDofusUnity.main.run_export_signature_overrides"),
            patch(_RUN_PIPELINE),
            pytest.raises(SystemExit, match="Invalid --field-mapping value"),
        ):
            _gen_new_msg(arguments)
