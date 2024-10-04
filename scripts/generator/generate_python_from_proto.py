import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.consts import PROTO_ROOT_PATH


def generate_python_from_protoc(input_folder: str, output_folder: str):
    file_paths: list[str] = []
    for directory, _, files in os.walk(input_folder):
        for file in files:
            if not file.endswith(".proto"):
                continue
            file_path = os.path.join(directory, file)
            file_paths.append(file_path)

    for file_path in file_paths:
        os.system(
            f"protoc --proto_path={Path(PROTO_ROOT_PATH).parent} --python_out={output_folder} {file_path} --pyi_out={output_folder}"
        )


if __name__ == "__main__":
    generate_python_from_protoc(PROTO_ROOT_PATH, str(Path(PROTO_ROOT_PATH).parent))
