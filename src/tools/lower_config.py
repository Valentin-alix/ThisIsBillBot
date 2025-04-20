import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from consts import PROJECT_ROOT

from src.const import RESOURCE_FOLDER

RELEASE_FOLDER = os.path.join(
    os.environ["USERPROFILE"], "AppData", "LocalLow", "Ankama", "Dofus", "RELEASE"
)
DOFUS_SHARED_PATH = os.path.join(RELEASE_FOLDER, "Shared", "dofus.json")
ACCOUNT_PATHS = os.path.join(RELEASE_FOLDER, "Accounts")


CUSTOM_CONFIG_FOLDER = os.path.join(RESOURCE_FOLDER, "dofus_config")
CUSTOM_SHARED_PATH = os.path.join(CUSTOM_CONFIG_FOLDER, "shared.json")
CUSTOM_DOFUS_PATH = os.path.join(CUSTOM_CONFIG_FOLDER, "dofus.json")
CUSTOM_DOFUS_UID_PATH = os.path.join(CUSTOM_CONFIG_FOLDER, "[uid]_dofus.json")


def set_config_key_values(path: str, override_json_path: str):
    with open(override_json_path) as config_file:
        override_config: dict[str, Any] = json.load(config_file)

    with open(path, "r") as file:
        try:
            content: dict[str, Any] = json.load(file)
        except json.JSONDecodeError:
            content = {}

    for key, value in override_config.items():
        content[key] = value

    with open(path, "w") as file:
        json.dump(content, file)


def set_low_config_for_all():
    set_config_key_values(DOFUS_SHARED_PATH, CUSTOM_SHARED_PATH)
    for acc_folder in os.listdir(ACCOUNT_PATHS):
        set_config_key_values(
            os.path.join(ACCOUNT_PATHS, acc_folder, "dofus.json"), CUSTOM_DOFUS_PATH
        )
        for root, _, files in os.walk(
            os.path.join(ACCOUNT_PATHS, acc_folder, "Characters")
        ):
            for file in files:
                if file == "dofus.json":
                    set_config_key_values(
                        os.path.join(root, file), CUSTOM_DOFUS_UID_PATH
                    )


if __name__ == "__main__":
    # dans dofus.json
    # "windowDisplayMode": {
    #     "value": 0
    # },
    # "windowResolutionMode": {
    #     "value": 14
    # },
    set_low_config_for_all()
