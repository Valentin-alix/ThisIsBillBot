import hashlib
from pathlib import Path

from DBDofusUnity.consts import OBF_PROTO_OUTPUT


def get_obfuscated_proto_schema_fingerprint(proto_directory: Path = OBF_PROTO_OUTPUT) -> str:
    proto_files = sorted(proto_directory.rglob("*.proto"))
    if not proto_files:
        raise FileNotFoundError(f"No obfuscated protobuf schema files found in {proto_directory}")

    fingerprint = hashlib.sha256()
    for proto_file in proto_files:
        relative_path = proto_file.relative_to(proto_directory).as_posix().encode("utf-8")
        content = proto_file.read_bytes()
        fingerprint.update(len(relative_path).to_bytes(8, byteorder="big"))
        fingerprint.update(relative_path)
        fingerprint.update(len(content).to_bytes(8, byteorder="big"))
        fingerprint.update(content)
    return fingerprint.hexdigest()
