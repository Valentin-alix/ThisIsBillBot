from pathlib import Path

from proto_mapper_assembly.interfaces.assembly_access import (
    AccessTraceDocument,
    ProtoAccessesInfo,
)


def parse_access_trace_document(path: str) -> AccessTraceDocument:
    with Path(path).open(encoding="utf-8") as file:
        return AccessTraceDocument.model_validate_json(file.read())


def parse_proto_accesses(path: str) -> ProtoAccessesInfo:
    return parse_access_trace_document(path).to_proto_accesses()
