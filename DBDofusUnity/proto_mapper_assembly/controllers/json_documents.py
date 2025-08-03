from pathlib import Path
from typing import Any

from pydantic import RootModel


def load_root_model_or_empty[RootDocumentT: RootModel[Any]](
    path: Path, document_type: type[RootDocumentT]
) -> RootDocumentT:
    if not path.exists():
        return document_type(root={})
    return document_type.model_validate_json(path.read_text(encoding="utf-8"))
