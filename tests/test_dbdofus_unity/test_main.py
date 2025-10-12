from __future__ import annotations

from unittest.mock import patch

from DBDofusUnity.main import build_argument_parser

_RUN_PIPELINE = "DBDofusUnity.proto_mapper_assembly.pipeline.run_pipeline"


class TestSynchronizeProtosCommand:
    def test_synchronize_protos_command_chains_all_steps(self) -> None:
        arguments = build_argument_parser().parse_args(["synchronize-protos"])

        with (
            patch("DBDofusUnity.main.gen_python") as gen_python,
            patch("DBDofusUnity.main.validate_unknown_names") as validate_unknown_names,
            patch("DBDofusUnity.main.synchronize_non_obf_mapping_artifacts") as synchronize_artifacts,
            patch("DBDofusUnity.main.run_export_signature_overrides") as run_export_signature_overrides,
            patch(_RUN_PIPELINE) as run_pipeline,
        ):
            arguments.handler(arguments)

        gen_python.assert_called_once_with(arguments)
        validate_unknown_names.assert_called_once_with()
        synchronize_artifacts.assert_called_once_with()
        run_export_signature_overrides.assert_called_once_with()
        run_pipeline.assert_called_once_with(do_load_pinned_pair=True)
