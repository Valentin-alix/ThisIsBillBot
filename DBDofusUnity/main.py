from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from DBDofusUnity.proto_mapper_assembly.scripts.add_to_new_dump_cs import (
    synchronize_non_obf_mapping_artifacts,
)
from DBDofusUnity.proto_mapper_assembly.scripts.dump import (
    _build_proto_dump_target,
    gen_python_from_protoc,
    update_protos,
)
from DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides import (
    run_export_signature_overrides,
)
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.main import run_ida_script
from DBDofusUnity.proto_mapper_assembly.scripts.unknown_name_registry import validate_unknown_names


def gen_python(_):
    target = _build_proto_dump_target(use_obf=False)
    if target.proto_output.is_file():
        python_output_folder = target.proto_output.parent
    else:
        python_output_folder = target.proto_output
    gen_python_from_protoc(target.proto_output, python_output_folder)


def _synchronize_protos(arguments: argparse.Namespace) -> None:
    # `gen_python` rewrites the *_pb2 modules on disk, so nothing that imports them may be
    # loaded before it runs: the stale descriptors would already sit in the default pool and
    # protobuf then rejects the regenerated ones with "duplicate file name <x>.proto".
    # This is why `run_pipeline` is imported below rather than at module level.
    gen_python(arguments)
    validate_unknown_names()
    synchronize_non_obf_mapping_artifacts()
    run_export_signature_overrides()

    from DBDofusUnity.proto_mapper_assembly.pipeline import run_pipeline

    run_pipeline(do_load_pinned_pair=True)


def new_maj_update_command(_):
    from DBDofusUnity.dofus_unity_reader.get_datas import update_all_datas

    update_all_datas()
    update_protos(use_obf=True)


def run_ida_script_command(arguments: argparse.Namespace):
    target = _build_proto_dump_target(use_obf=not arguments.non_obf)
    run_ida_script(
        use_non_obf=arguments.non_obf, base_dir=target.output_folder, database_path=target.ida_database
    )


def _run_pipeline_command(arguments: argparse.Namespace) -> None:
    from DBDofusUnity.proto_mapper_assembly.pipeline import run_pipeline

    run_pipeline(do_load_pinned_pair=not arguments.no_pinned, obf_dir=arguments.obf_dir)


def build_argument_parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description="DBDofusUnity maintenance commands.")
    subparsers = argument_parser.add_subparsers(dest="command", required=False)

    pipeline_parser = subparsers.add_parser("run-pipeline", help="Run the proto mapping pipeline.")
    pipeline_parser.add_argument(
        "--no-pinned", action="store_true", default=False, help="Update obfuscated protocol artifacts."
    )
    pipeline_parser.add_argument(
        "--obf-dir",
        type=Path,
        help="Use this obfuscated dump folder for obf inputs, pinned data, overrides, and game mappings.",
    )
    pipeline_parser.set_defaults(handler=_run_pipeline_command)

    synchronize_protos_parser = subparsers.add_parser(
        "synchronize-protos",
        help="Regenerate every non-obfuscated protobuf artifact and run the mapping pipeline.",
    )
    synchronize_protos_parser.set_defaults(handler=_synchronize_protos)

    on_new_maj_parser = subparsers.add_parser(
        "update-maj", help="Execute at a new dofus maj <!> it reset pinned_pairs & instancied_msg_info.json"
    )
    on_new_maj_parser.set_defaults(handler=new_maj_update_command)

    ida_parser = subparsers.add_parser("ida", help="Run ida pipeline")
    ida_parser.add_argument("--non-obf", action="store_true", default=False)
    ida_parser.set_defaults(handler=run_ida_script_command)

    return argument_parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_argument_parser()
    arguments = parser.parse_args(argv)
    # set default to run-pipeline if no arg provided
    if arguments.command is None:
        arguments = parser.parse_args(["run-pipeline"])
    arguments.handler(arguments)


if __name__ == "__main__":
    main()
