import os
from pathlib import Path

from pydantic import ValidationError
from src.utils.runtime_support import RuntimeSetupError

from ankama_launcher_emulator.interfaces.ankama_release import (
    ReleaseJson,
)


def resolve_dofus_path() -> str:
    path = Path(RELEASE_JSON_PATH)
    if not path.is_file():
        raise RuntimeSetupError("Dofus is missing: install Dofus Unity with the Ankama launcher.")
    try:
        release = ReleaseJson.model_validate_json(path.read_text(encoding="utf-8"))
    except (ValidationError, UnicodeError) as error:
        raise RuntimeSetupError(
            "Dofus release.json is invalid. Repair the installation with the Ankama launcher."
        ) from error
    executable = Path(release.location) / "Dofus.exe"
    if not executable.is_file():
        raise RuntimeSetupError(
            "The saved Dofus path is outdated. Repair the installation with the Ankama launcher."
        )
    return str(executable)


def _get_zaap_path() -> Path:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "zaap"
    config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(config_home) / "zaap"


ZAAP_PATH = _get_zaap_path()
RELEASE_JSON_PATH = os.path.join(ZAAP_PATH, "repositories", "production", "dofus", "dofus3", "release.json")


def _get_app_config_dir() -> Path:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "AnkamaLauncherEmulator"
    config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(config_home) / "AnkamaLauncherEmulator"


app_config_dir = _get_app_config_dir()
os.makedirs(app_config_dir, exist_ok=True)
