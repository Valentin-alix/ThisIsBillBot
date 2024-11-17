import json
import os
from typing import Any

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
CUSTOM_PRESET_PATH = os.path.join(CUSTOM_CONFIG_FOLDER, "preset.json")


def set_config_key_values(path: str, path_config: str):
    with open(path_config) as config_file:
        config: dict = json.load(config_file)

    with open(path, "r") as file:
        try:
            content: dict[str, Any] = json.load(file)
        except json.JSONDecodeError:
            content = {}

    for key, value in config.items():
        content[key] = value

    with open(path, "w+") as file:
        json.dump(content, file)


def set_low_config_for_all():
    set_config_key_values(DOFUS_SHARED_PATH, CUSTOM_SHARED_PATH)
    for acc_folder in os.listdir(ACCOUNT_PATHS):
        set_config_key_values(
            os.path.join(ACCOUNT_PATHS, acc_folder, "dofus.json"), CUSTOM_DOFUS_PATH
        )
        set_config_key_values(
            os.path.join(ACCOUNT_PATHS, acc_folder, "preset.json"), CUSTOM_PRESET_PATH
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
    set_low_config_for_all()
