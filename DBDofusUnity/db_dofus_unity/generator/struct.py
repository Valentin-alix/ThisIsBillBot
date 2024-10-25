import os
from pathlib import Path
import re


def to_snake_case(value: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def run_cmd_codegen(input_filename: str, output_filename: str, class_name: str) -> None:
    cmd = (
        f"datamodel-codegen --input-file-type json --input {input_filename} --output {output_filename} --custom"
        f"-template-dir {os.path.join(Path(__file__).parent, 'template')}  --output-model-type msgspec.Struct "
        f"--encoding utf-8 --target-python-version 3.12 --keyword-only --class-name {class_name}"
    )
    os.system(cmd)


def gen_model(input_folder: str, filename: str, output_folder: str):
    file_path = os.path.join(input_folder, filename)
    class_name = filename.replace(".json", "")
    print(f"gen model from {class_name}")
    python_filename = to_snake_case(filename).split(".json")[0] + ".py"
    run_cmd_codegen(file_path, os.path.join(output_folder, python_filename), class_name)
