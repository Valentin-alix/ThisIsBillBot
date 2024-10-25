import zlib
from typing import Any

import msgspec.json


def clean_data_to_output(class_type: Any, filepath: str):
    with open(filepath, "rb") as file:
        content = msgspec.json.decode(file.read(), type=class_type)

    with open(filepath, "wb") as file:
        file.write(
            zlib.compress(msgspec.json.encode(content), level=zlib.Z_BEST_COMPRESSION)
        )
