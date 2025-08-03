from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from consts import PINNED_PAIRS_FILE
from proto_mapper_assembly.controllers.pinned_pairs import upsert_pinned_field_mapping, upsert_pinned_pair
from proto_mapper_assembly.scripts.add_to_new_dump_cs import build_new_dump_cs_entries
from proto_mapper_assembly.scripts.dump import _build_proto_dump_target, gen_python_from_protoc, update_protos
from proto_mapper_assembly.scripts.export_signature_overrides import run_export_signature_overrides
from proto_mapper_assembly.scripts.ida_tracer_lib.main import run_ida_script


def gen_python(_):
    target = _build_proto_dump_target(use_obf=False)
    if target.proto_output.is_file():
        python_output_folder = target.proto_output.parent
    else:
        python_output_folder = target.proto_output
    gen_python_from_protoc(target.proto_output, python_output_folder)


def _gen_new_msg(arguments: argparse.Namespace) -> None:
    # `gen_python` rewrites the *_pb2 modules on disk, so nothing that imports them may be
    # loaded before it runs: the stale descriptors would already sit in the default pool and
    # protobuf then rejects the regenerated ones with "duplicate file name <x>.proto".
    # This is why `run_pipeline` is imported below rather than at module level.
    gen_python(arguments)
    build_new_dump_cs_entries([arguments.class_name])

    upsert_pinned_pair(PINNED_PAIRS_FILE, arguments.obf_class_name, arguments.class_name)

    for field_mapping in arguments.field_mappings:
        obf_field_name, separator, non_obf_field_name = field_mapping.partition("=")
        if not separator:
            err = f"Invalid --field-mapping value {field_mapping!r}; expected OBF_FIELD=NON_OBF_FIELD."
            raise SystemExit(err)
        upsert_pinned_field_mapping(
            PINNED_PAIRS_FILE,
            arguments.obf_class_name,
            arguments.class_name,
            obf_field_name,
            non_obf_field_name,
        )

    run_export_signature_overrides()

    from proto_mapper_assembly.pipeline import run_pipeline

    run_pipeline(do_load_pinned_pair=True)


def new_maj_update_command(_):
    from dofus_unity_reader.get_datas import update_all_datas

    update_all_datas()
    update_protos(use_obf=True)


def run_ida_script_command(arguments: argparse.Namespace):
    target = _build_proto_dump_target(use_obf=not arguments.non_obf)
    run_ida_script(
        use_non_obf=arguments.non_obf, base_dir=target.output_folder, database_path=target.ida_database
    )


def _run_pipeline_command(arguments: argparse.Namespace) -> None:
    from proto_mapper_assembly.pipeline import run_pipeline

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

    gen_new_non_obf_msg = subparsers.add_parser(
        "gen-msg",
        help="Run when added a new msg in .proto: gen python, register in new_dump_cs.json, "
        "pin the obf pair, export overrides, run the pipeline.",
    )
    gen_new_non_obf_msg.add_argument(
        "class_name",
        help="Composed non-obf class name to add/overwrite in new_dump_cs.json and to pin as the "
        "non-obf target.",
    )
    gen_new_non_obf_msg.add_argument(
        "--obf",
        dest="obf_class_name",
        required=True,
        help="Obfuscated short class name to pin against the non-obf target.",
    )
    gen_new_non_obf_msg.add_argument(
        "--field-mapping",
        dest="field_mappings",
        action="append",
        default=[],
        metavar="OBF_FIELD=NON_OBF_FIELD",
        help="Repeatable pinned field-mapping override (obf field name = non-obf field name).",
    )
    gen_new_non_obf_msg.set_defaults(handler=_gen_new_msg)

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
