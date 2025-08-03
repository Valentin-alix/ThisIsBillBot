import json
from pathlib import Path
from typing import Any

import msgspec
import msgspec.json


def clean_data_to_output(class_type: type[Any], filepath: Path) -> None:
    with filepath.open("rb") as file:
        content = msgspec.json.decode(file.read(), type=class_type)

    cleaned_content = f"{json.dumps(msgspec.to_builtins(content), indent=2, ensure_ascii=False)}\n"
    if filepath.exists() and filepath.read_text(encoding="utf-8") == cleaned_content:
        return

    filepath.write_text(cleaned_content, encoding="utf-8")
