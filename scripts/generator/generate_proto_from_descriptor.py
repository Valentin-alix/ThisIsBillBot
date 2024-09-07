import json
import os
import shutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.generator.consts import DESCRIPTOR_FOLDER, PROTO_FOLDER
from scripts.generator.models.descriptor import (
    Descriptor,
)


def generate_proto_files(input_descriptor_folder: str, output_folder: str):
    shutil.rmtree(output_folder, ignore_errors=True)

    for filename in os.listdir(input_descriptor_folder):
        with open(os.path.join(input_descriptor_folder, filename), "r") as file:
            descriptor = Descriptor.model_validate(json.load(file))

        if descriptor.package is None:
            continue

        proto_folder_output = os.path.join(
            PROTO_FOLDER, "/".join(filename.split(".")[:-2]).lower()
        )
        proto_file_path = filename.split(".")[-2].lower() + ".proto"
        os.makedirs(proto_folder_output, exist_ok=True)

        with open(
            os.path.join(proto_folder_output, proto_file_path).lower(), "w"
        ) as file:
            file.write(descriptor.get_content())


if __name__ == "__main__":
    generate_proto_files(DESCRIPTOR_FOLDER, PROTO_FOLDER)
