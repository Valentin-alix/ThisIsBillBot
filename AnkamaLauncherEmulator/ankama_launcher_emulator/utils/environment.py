import os
from pathlib import Path

from pydantic import ValidationError

from ankama_launcher_emulator.interfaces.ankama_release import (
    ReleaseJson,
)


def _read_release_executable_path(release_json_path: str, executable_name: str) -> str | None:
    if not os.path.exists(release_json_path):
        return None
    with open(release_json_path, encoding="utf-8") as file:
        text = file.read()
    try:
        release = ReleaseJson.model_validate_json(text)
    except ValidationError:
        return None
    return os.path.join(release.location, executable_name)


def _get_zaap_path() -> Path:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "zaap"
    config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(config_home) / "zaap"


ZAAP_PATH = _get_zaap_path()
RELEASE_JSON_PATH = os.path.join(ZAAP_PATH, "repositories", "production", "dofus", "dofus3", "release.json")
DOFUS_PATH = _read_release_executable_path(RELEASE_JSON_PATH, "Dofus.exe") or "DUMMY_PATH"
DOFUS_INSTALLED = os.path.exists(DOFUS_PATH)


def _get_app_config_dir() -> Path:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "AnkamaLauncherEmulator"
    config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(config_home) / "AnkamaLauncherEmulator"


app_config_dir = _get_app_config_dir()
os.makedirs(app_config_dir, exist_ok=True)
