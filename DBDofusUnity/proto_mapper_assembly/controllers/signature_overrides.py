from pathlib import Path

from DBDofusUnity.proto_mapper_assembly.controllers.json_documents import load_root_model_or_empty
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import SignatureOverridesFile


def load_signature_overrides(path: Path) -> SignatureOverridesFile:
    return load_root_model_or_empty(path, SignatureOverridesFile)
