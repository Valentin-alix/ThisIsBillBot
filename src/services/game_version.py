from pathlib import Path
from typing import Annotated

import requests
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from ankama_launcher_emulator.interfaces.ankama_release import ReleaseJson
from ankama_launcher_emulator.utils.environment import RELEASE_JSON_PATH
from src.utils.project_paths import BUNDLE_ROOT
from src.utils.runtime_support import RuntimeSetupError

CYTRUS_URL = "https://cytrus.cdn.ankama.com/cytrus.json"
VERSION_PATH = BUNDLE_ROOT / "VERSION"
GameVersion = Annotated[str, Field(strict=True, pattern=r"^\d+\.\d+_\d+\.\d+\.\d+\.\d+$")]


class WindowsReleases(BaseModel):
    dofus3: GameVersion


class Platforms(BaseModel):
    windows: WindowsReleases


class DofusRelease(BaseModel):
    platforms: Platforms


class Games(BaseModel):
    dofus: DofusRelease


class CytrusIndex(BaseModel):
    games: Games


def validate_game_version() -> None:
    try:
        release = ReleaseJson.model_validate_json(Path(RELEASE_JSON_PATH).read_bytes())
        installed = TypeAdapter[str](GameVersion).validate_python(release.version)
    except (OSError, ValidationError) as error:
        raise RuntimeSetupError(
            "The installed Dofus version is missing or unreadable. "
            "Repair the installation with the Ankama launcher."
        ) from error
    try:
        compatible = TypeAdapter[str](GameVersion).validate_python(
            VERSION_PATH.read_text(encoding="utf-8").strip()
        )
    except (OSError, UnicodeError, ValidationError) as error:
        raise RuntimeSetupError(
            "The bot VERSION file is missing or invalid. Reinstall the bot."
        ) from error
    try:
        with requests.get(CYTRUS_URL, timeout=10) as response:
            response.raise_for_status()
            latest = CytrusIndex.model_validate_json(response.content).games.dofus.platforms.windows.dofus3
    except (requests.RequestException, ValidationError) as error:
        raise RuntimeSetupError(
            "Unable to check the game version. Check your connection and try again. "
            "Startup was interrupted."
        ) from error

    versions = (
        f"\n\nInstalled version: {installed}\n"
        f"Bot-compatible version: {compatible}\n"
        f"Available version: {latest}"
    )
    messages: list[str] = []
    if installed != latest:
        messages.append(
            "Dofus is out of date. Update the game with the Ankama launcher before restarting the bot."
        )
    if compatible != installed or compatible != latest:
        messages.append(
            "The bot is out of date for this Dofus version. Install a compatible bot version."
        )
    if messages:
        raise RuntimeSetupError("\n\n".join(messages) + versions)
