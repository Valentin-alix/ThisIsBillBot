import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(os.path.join(Path(__file__).parent.parent.parent, ".env"))


sys.path.append(os.path.join(Path(__file__).parent.parent.parent))
sys.path.append(os.path.join(Path(__file__).parent.parent.parent, "D3Mapping"))
sys.path.append(os.path.join(Path(__file__).parent.parent.parent, "DBDofusUnity"))
sys.path.append(os.path.join(Path(__file__).parent.parent.parent, "D3Database"))


from d3_mapping.consts import (  # noqa: E402
    ASSEMBLIES_PATH,
    GAME_ASSEMBLY_PATH,
    GLOBAL_METADATA_PATH,
    IL2_CPP_DUMPER_PATH_EXE,
    OBFUSCATED_PROTO_CONNECTION_FILE,
    OBFUSCATED_PROTO_GAME_FILE,
    PROTO_CONNECTION_ASSEMBLY_PATH,
    PROTO_CONNECTION_PATH,
    PROTO_GAME_ASSEMBLY_PATH,
    PROTO_GAME_PATH,
    PROTODEC_PATH_EXE,
)
from d3_mapping.controller.instancied_msg_info_controller import (  # noqa: E402
    InstanciedMessageInfoController,
)
from d3_mapping.controller.message_mapping_controller import (  # noqa: E402
    MessageMappingController,
)
from d3_mapping.mapping.gen_mapping_proto import generate_all_mapping  # noqa: E402


def get_obf_protos():
    get_assemblies()
    get_protos()


def get_assemblies():
    os.makedirs(ASSEMBLIES_PATH, exist_ok=True)
    command = f"{IL2_CPP_DUMPER_PATH_EXE} {GAME_ASSEMBLY_PATH} {GLOBAL_METADATA_PATH} {ASSEMBLIES_PATH}"
    os.system(command)


def get_protos():
    os.system(
        f"{PROTODEC_PATH_EXE} {PROTO_CONNECTION_ASSEMBLY_PATH} {OBFUSCATED_PROTO_CONNECTION_FILE}"
    )
    os.system(
        f"{PROTODEC_PATH_EXE} {PROTO_GAME_ASSEMBLY_PATH} {OBFUSCATED_PROTO_GAME_FILE}"
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
            os.system(
                f"protoc --proto_path={input} --python_out={output_folder} {file_path} --pyi_out={output_folder}"
            )
    else:
        os.system(
            f"protoc --proto_path={Path(input).parent} --python_out={Path(input).parent} {input} --pyi_out={Path(input).parent}"
        )


def is_new_version():
    return MessageMappingController().get_mapping_game_version() != os.path.getmtime(
        GAME_ASSEMBLY_PATH
    )


def init_mapping_resources():
    if not is_new_version():
        return
    print("Getting new protos...")
    get_obf_protos()
    print("Clearing msg infos")
    InstanciedMessageInfoController().clear()


def update_proto_on_new_version():
    init_mapping_resources()
    gen_all_python_from_obf_protoc()
    generate_all_mapping()


if __name__ == "__main__":
    # gen_all_python_from_protoc()
    generate_all_mapping()
