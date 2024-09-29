import os
from pathlib import Path
import sys


sys.path.append(str(Path(__file__).parent.parent.parent))

from src.consts import DOFUS_DATA_PATH, USEFUL_DATAS_JSON
from src.consts import OUTPUT_CLASS_DATAS

if __name__ == "__main__":
    for filename in os.listdir(DOFUS_DATA_PATH):
        if not filename.endswith(".json") or filename not in USEFUL_DATAS_JSON.values():
            continue
        file_path = os.path.join(DOFUS_DATA_PATH, filename)

        python_filename = filename.split(".json")[0] + ".py"
        cmd = f"datamodel-codegen --input-file-type json --input {file_path} --output {os.path.join(OUTPUT_CLASS_DATAS, python_filename)} --output-model-type typing.TypedDict"
        os.system(cmd)
