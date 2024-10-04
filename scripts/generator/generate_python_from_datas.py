import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.consts import (
    WORLD_GRAPH_FILENAME,
    DOFUS_FOLDER,
    OUTPUT_CLASS_DATAS,
    DOFUS_DATA_PATH,
    DOFUS_MAP_PATH,
    DOFUS_STANDALONE_PATH,
    OUTPUT_CLASS_MAPS,
    OUTPUT_CLASS_STANDALONE,
)


def run_cmd_codegen(
    input_filename: str,
    output_filename: str,
    class_name: str,
    base_dofus_folder: str | None = None,
):
    cmd = f"datamodel-codegen --class-name {class_name} --input-file-type json --input {input_filename} --output {output_filename} --custom-template-dir template  --output-model-type msgspec.Struct"
    if base_dofus_folder:
        extra_data = {class_name: {}, "#all#": {}}
        filepath = os.path.relpath(input_filename, base_dofus_folder)
        extra_data[class_name]["filepath"] = filepath
        with NamedTemporaryFile(mode="r+", suffix=".json", delete=False) as file:
            json.dump(extra_data, file)
        cmd += f" --extra-template-data {file.name}"
    os.system(cmd)


def gen_datas(base_dofus_folder: str, input_folder: str, output_folder: str):
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"):
            continue
        print(f"processing data {filename}")
        file_path = os.path.join(input_folder, filename)
        class_name = filename.split(".json")[0].replace("Root", "Model")
        python_filename = filename.split(".json")[0] + ".py"
        run_cmd_codegen(
            file_path,
            os.path.join(output_folder, python_filename),
            class_name,
            base_dofus_folder,
        )


def gen_map_datas(input_folder: str, output_folder: str):
    for filename in os.listdir(input_folder):
        if not filename.startswith("map_") or not filename.endswith(".json"):
            continue
        print(f"processing map {filename}")
        file_path = os.path.join(input_folder, filename)
        class_name = "MapsModel"
        run_cmd_codegen(
            file_path, os.path.join(output_folder, "MapsRoot.py"), class_name
        )
        break


def gen_world_graph_datas(
    base_dofus_folder: str, input_folder: str, output_folder: str
):
    file_path = os.path.join(input_folder, WORLD_GRAPH_FILENAME)
    print("processing world graph")
    class_name = "WorldGraphModel"
    run_cmd_codegen(
        file_path,
        os.path.join(output_folder, "WorldGraphRoot" + ".py"),
        class_name,
        base_dofus_folder,
    )


if __name__ == "__main__":
    gen_datas(DOFUS_FOLDER, DOFUS_DATA_PATH, OUTPUT_CLASS_DATAS)
    gen_world_graph_datas(DOFUS_FOLDER, DOFUS_STANDALONE_PATH, OUTPUT_CLASS_STANDALONE)
    gen_map_datas(DOFUS_MAP_PATH, OUTPUT_CLASS_MAPS)
