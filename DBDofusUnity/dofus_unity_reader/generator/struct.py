import re
import shutil
import subprocess
from pathlib import Path


def to_snake_case(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def run_cmd_codegen(input_filename: str, output_filename: str, class_name: str) -> None:
    template_dir = Path(__file__).parent / "template"
    executable = shutil.which("datamodel-codegen")
    if executable is None:
        message = "datamodel-codegen executable not found"
        raise FileNotFoundError(message)
    subprocess.run(
        [
            executable,
            "--input-file-type",
            "json",
            "--input",
            input_filename,
            "--output",
            output_filename,
            "--custom-template-dir",
            str(template_dir),
            "--output-model-type",
            "msgspec.Struct",
            "--encoding",
            "utf-8",
            "--target-python-version",
            "3.12",
            "--keyword-only",
            "--class-name",
            class_name,
        ],
        check=True,
    )


def gen_model(input_folder: str, filename: str, output_folder: str) -> None:
    class_name = filename.replace(".json", "")
    print(f"gen model from {class_name}")
    file_path = Path(input_folder) / filename
    python_filename = to_snake_case(filename).split(".json")[0] + ".py"
    run_cmd_codegen(str(file_path), str(Path(output_folder) / python_filename), class_name)
