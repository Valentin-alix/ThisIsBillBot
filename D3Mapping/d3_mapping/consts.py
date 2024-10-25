import os
from pathlib import Path

from D3Database.consts import DOFUS_PATH

IL2_CPP_DUMPER_PATH_EXE = os.path.join(
    Path(__file__).parent.parent,
    "Il2CppDumper",
    "Il2CppDumper",
    "bin",
    "Debug",
    "net8.0",
    "IL2CppDumper.exe",
)
PROTODEC_PATH_EXE = os.path.join(
    Path(__file__).parent.parent,
    "protodec",
    "bin",
    "protodec",
    "Debug",
    "net8.0",
    "protodec.exe",
)

ASSEMBLIES_PATH = os.path.join(DOFUS_PATH, "assemblies")
GAME_ASSEMBLY_PATH = os.path.join(DOFUS_PATH, "GameAssembly.dll")
GLOBAL_METADATA_PATH = os.path.join(
    DOFUS_PATH, "Dofus_Data", "il2cpp_data", "Metadata", "global-metadata.dat"
)


PROTO_CONNECTION_ASSEMBLY_PATH = os.path.join(
    ASSEMBLIES_PATH, "DummyDll", "Ankama.Dofus.Protocol.Connection.dll"
)
PROTO_GAME_ASSEMBLY_PATH = os.path.join(
    ASSEMBLIES_PATH, "DummyDll", "Ankama.Dofus.Protocol.Game.dll"
)


ROOT_PATH = Path(__file__).parent.parent

IL2CPP_EXTRACT_PATH = os.path.join(ROOT_PATH, "IL2CppExtract", "IL2CppExtract")
UNITY_MAPPER_PATH = os.path.join(ROOT_PATH, "IL2CppExtract", "UnityMapper")

RESOURCE_PATH = os.path.join(ROOT_PATH, "d3_mapping", "resources")

OBFUSCATED_PROTOS = os.path.join(RESOURCE_PATH, "obf_protos")
OBFUSCATED_PROTO_CONNECTION = os.path.join(OBFUSCATED_PROTOS, "connection")
OBFUSCATED_PROTO_CONNECTION_FILE = os.path.join(
    OBFUSCATED_PROTO_CONNECTION, "connection_messages.proto"
)
OBFUSCATED_PROTO_GAME = os.path.join(OBFUSCATED_PROTOS, "game")
OBFUSCATED_PROTO_GAME_FILE = os.path.join(OBFUSCATED_PROTO_GAME, "game_messages.proto")

PROTO_ROOT_PATH = os.path.join(RESOURCE_PATH, "protos")
PROTO_CONNECTION_PATH = os.path.join(PROTO_ROOT_PATH, "connection")
PROTO_GAME_PATH = os.path.join(PROTO_ROOT_PATH, "game")

MAPPING_CONN_PROTO_PATH = os.path.join(RESOURCE_PATH, "connection_mappings.json")
MAPPING_GAME_PROTO_PATH = os.path.join(RESOURCE_PATH, "game_mappings.json")
