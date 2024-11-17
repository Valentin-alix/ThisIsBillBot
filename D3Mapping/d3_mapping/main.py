import json
import os
import subprocess
import sys
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from icecream import ic
from tqdm import tqdm

from D3Mapping.d3_mapping.factories.p_mapper_factory import PMapperFactory
from D3Mapping.d3_mapping.mapping.debug_messages import diff_output_field_mappings
from D3Mapping.d3_mapping.models.mapping_info import OutputMappingInfo
from D3Mapping.d3_mapping.models.p_message import PMessage
from D3Mapping.d3_mapping.models.verified_mapping import VerifiedMapping
from D3Mapping.d3_mapping.verified_mapping import (
    GAME_VERIFIED_MAPPING,
    GAME_VERIFIED_MAPPING_BY_OBF,
)

load_dotenv(os.path.join(Path(__file__).parent.parent.parent, ".env"))


sys.path.append(os.path.join(Path(__file__).parent.parent.parent))


from D3Mapping.d3_mapping.consts import (
    ASSEMBLIES_PATH,  # noqa: E402
    GAME_ASSEMBLY_PATH,
    GLOBAL_METADATA_PATH,
    IL2_CPP_DUMPER_PATH_EXE,
    MAPPING_CONN_AUDIT_PATH,
    MAPPING_CONN_PROTO_PATH,
    MAPPING_GAME_AUDIT_PATH,
    MAPPING_GAME_PROTO_PATH,
    MSG_TO_MAP,
    OBFUSCATED_PROTO_CONNECTION,
    OBFUSCATED_PROTO_CONNECTION_FILE,
    OBFUSCATED_PROTO_GAME,
    OBFUSCATED_PROTO_GAME_FILE,
    PROTO_CONNECTION_ASSEMBLY_PATH,
    PROTO_CONNECTION_PATH,
    PROTO_GAME_ASSEMBLY_PATH,
    PROTO_GAME_PATH,
    PROTODEC_PATH_EXE,
    UNMAPPED_CANDIDATES_PATH,
)
from D3Mapping.d3_mapping.controller.instancied_msg_info_controller import (
    InstanciedMessageInfoController,  # noqa: E402
)
from D3Mapping.d3_mapping.controller.message_mapping_controller import (
    MessageMappingController,  # noqa: E402
)


def get_obf_protos():
    get_assemblies()
    get_protos()


def get_assemblies():
    os.makedirs(ASSEMBLIES_PATH, exist_ok=True)
    subprocess.run(
        [
            IL2_CPP_DUMPER_PATH_EXE,
            GAME_ASSEMBLY_PATH,
            GLOBAL_METADATA_PATH,
            ASSEMBLIES_PATH,
        ],
        check=True,
    )


def get_protos():
    subprocess.run(
        [
            PROTODEC_PATH_EXE,
            PROTO_CONNECTION_ASSEMBLY_PATH,
            OBFUSCATED_PROTO_CONNECTION_FILE,
        ],
        check=True,
    )
    subprocess.run(
        [PROTODEC_PATH_EXE, PROTO_GAME_ASSEMBLY_PATH, OBFUSCATED_PROTO_GAME_FILE],
        check=True,
    )


def gen_all_python_from_protoc():
    gen_python_from_protoc(PROTO_CONNECTION_PATH, PROTO_CONNECTION_PATH)
    gen_python_from_protoc(PROTO_GAME_PATH, PROTO_GAME_PATH)


def gen_all_python_from_obf_protoc():
    gen_python_from_protoc(
        OBFUSCATED_PROTO_CONNECTION_FILE, OBFUSCATED_PROTO_CONNECTION_FILE
    )
    gen_python_from_protoc(OBFUSCATED_PROTO_GAME_FILE, OBFUSCATED_PROTO_GAME_FILE)


def gen_python_from_protoc(input: str, output_folder: str):
    if os.path.isdir(input):
        for filename in os.listdir(input):
            if not filename.endswith(".proto"):
                continue
            file_path = os.path.join(input, filename)
            subprocess.run(
                [
                    "protoc",
                    f"--proto_path={input}",
                    f"--python_out={output_folder}",
                    file_path,
                    f"--pyi_out={output_folder}",
                ],
                check=True,
            )
    else:
        parent = str(Path(input).parent)
        subprocess.run(
            [
                "protoc",
                f"--proto_path={parent}",
                f"--python_out={parent}",
                input,
                f"--pyi_out={parent}",
            ],
            check=True,
        )


def init_mapping_resources():
    print("Getting new protos...")
    get_obf_protos()
    print("Clearing msg infos")
    InstanciedMessageInfoController().clear()


def update_proto_on_new_version():
    init_mapping_resources()
    gen_all_python_from_obf_protoc()
    generate_all_mapping()


def generate_mapping_proto(
    clear_directory: str,
    obf_directory: str,
    output: str,
    audit_output: str,
    old_mapping_info: dict[str, OutputMappingInfo],
    verified_mapping: VerifiedMapping,
):
    mapper = PMapperFactory.create_p_mapper(
        clear_directory,
        obf_directory,
        verified_mapping=verified_mapping,
    )
    mapping = mapper.run_mapping()
    ic(diff_output_field_mappings(old_mapping_info, mapping))
    MessageMappingController.dump_mapping(mapping, output)
    MessageMappingController.dump_audit(
        mapper.audit_by_clear_namespace,
        mapper.metrics,
        audit_output,
    )


def generate_all_mapping():
    generate_mapping_proto(
        PROTO_CONNECTION_PATH,
        OBFUSCATED_PROTO_CONNECTION,
        MAPPING_CONN_PROTO_PATH,
        MAPPING_CONN_AUDIT_PATH,
        MessageMappingController.get_mapping_conn(),
        VerifiedMapping(verified_msg_by_obf={}, field_mappings={}),
    )
    generate_mapping_proto(
        PROTO_GAME_PATH,
        OBFUSCATED_PROTO_GAME,
        MAPPING_GAME_PROTO_PATH,
        MAPPING_GAME_AUDIT_PATH,
        MessageMappingController.get_mapping_game(),
        GAME_VERIFIED_MAPPING,
    )


def generate_filtered_mapping():
    used_fields = MessageMappingController.get_used_fields()
    full_mapping = MessageMappingController.get_mapping_game()
    filtered_mapping = MessageMappingController.filter_mapping_by_used_fields(
        full_mapping, used_fields
    )
    MessageMappingController.dump_mapping(filtered_mapping, MAPPING_GAME_PROTO_PATH)


def generate_unmapped_candidates():
    mapper = PMapperFactory.create_p_mapper(
        PROTO_GAME_PATH,
        OBFUSCATED_PROTO_GAME,
        verified_mapping=GAME_VERIFIED_MAPPING,
    )
    mapper._build_indices()

    already_mapped_clear_names = set(GAME_VERIFIED_MAPPING_BY_OBF.values())
    excluded_obf_namespaces = set(GAME_VERIFIED_MAPPING_BY_OBF.keys())
    unmapped_clear_names = [
        name for name in MSG_TO_MAP if name not in already_mapped_clear_names
    ]

    candidates: dict[str, list[dict[str, str | float]]] = {}
    for clear_name in tqdm(unmapped_clear_names):
        clear_namespace = cast(dict[str, str], mapper._clear_name_to_namespace).get(
            clear_name
        )
        if clear_namespace is None:
            print(f"Skipping {clear_name}: namespace not found")
            continue
        clear_struct = mapper.clear_struct_by_namespace.get(clear_namespace)
        if not isinstance(clear_struct, PMessage):
            continue

        top_matches = mapper.get_top_similar_obf_msgs(
            clear_struct, excluded_obf_namespaces=excluded_obf_namespaces
        )
        if top_matches:
            candidates[clear_name] = [
                {"obf_namespace": obf_ns, "similarity": round(sim, 4)}
                for sim, obf_ns, _ in top_matches
            ]

    with open(UNMAPPED_CANDIDATES_PATH, "w") as f:
        json.dump(candidates, f, indent=2)

    print(f"\nUnmapped candidates written to {UNMAPPED_CANDIDATES_PATH}")
    print(
        f"Found candidates for {len(candidates)}/{len(unmapped_clear_names)} unmapped messages"
    )


def main():
    # gen_all_python_from_protoc()
    # dump_all_used_fields()
    generate_all_mapping()
    generate_unmapped_candidates()


if __name__ == "__main__":
    main()
