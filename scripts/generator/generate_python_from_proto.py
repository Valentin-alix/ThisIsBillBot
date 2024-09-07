import os
import shutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.generator.consts import PROTO_FOLDER


def generate_python_from_protoc(input_folder: str):
    # delete old generated folder
    shutil.rmtree(
        os.path.join(Path(__file__).parent.parent.parent, "com"), ignore_errors=True
    )

    file_paths: list[str] = []
    for dir, _, files in os.walk(input_folder):
        for file in files:
            if not file.endswith(".proto"):
                continue
            file_path = os.path.join(dir, file)
            file_paths.append(file_path)

    # Workaround to protoc multiple files without having the command line is too large error
    CHUNK_SIZE = 50
    for group_index in range(0, len(file_paths), CHUNK_SIZE):
        os.system(
            f"protoc --proto_path={PROTO_FOLDER} --python_out=. {" ".join(file_paths[group_index : group_index + CHUNK_SIZE])} --pyi_out=."
        )


if __name__ == "__main__":
    generate_python_from_protoc(PROTO_FOLDER)
