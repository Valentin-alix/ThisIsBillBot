from pathlib import Path

from pydantic import BaseModel, ValidationError

from src.utils.runtime_support import RuntimeSetupError


def read_local_model[T: BaseModel](path: Path, model: type[T]) -> T:
    try:
        return model.model_validate_json(path.read_text(encoding="utf-8"))
    except (ValidationError, UnicodeError) as error:
        raise RuntimeSetupError(
            f"Invalid local file: {path.name}. Fix it or restore a backup."
        ) from error
