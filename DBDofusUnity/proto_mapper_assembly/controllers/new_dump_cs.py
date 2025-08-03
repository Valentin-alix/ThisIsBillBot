from pathlib import Path

from proto_mapper_assembly.controllers.json_documents import load_root_model_or_empty
from proto_mapper_assembly.interfaces.new_dump_cs import NewDumpCSFile


def load_new_dump_cs_messages(path: Path) -> NewDumpCSFile:
    return load_root_model_or_empty(path, NewDumpCSFile)
