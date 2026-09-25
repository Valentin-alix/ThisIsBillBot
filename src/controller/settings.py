import json
import os
from threading import RLock
from typing import cast

from ankama_launcher_emulator.utils.atomic_file import acquire_file_lock, atomic_write_text
from pydantic import ValidationError

from src.core.config import BehaviorSettings, GlobalSettings
from src.utils.project_paths import USER_DATA_ROOT
from src.utils.runtime_support import RuntimeSetupError
from utils.local_json import read_local_model
from utils.singleton import Singleton

SETTINGS_PATH = USER_DATA_ROOT / "resources" / "settings.json"


class SettingsService(metaclass=Singleton):
    def __init__(self) -> None:
        self._lock = RLock()
        self._settings: GlobalSettings | None = None

    def get(self) -> GlobalSettings:
        with self._lock:
            if self._settings is None:
                self._settings = (
                    self._load_settings()
                    if SETTINGS_PATH.exists()
                    else GlobalSettings()
                )
            return self._settings

    def _load_settings(self) -> GlobalSettings:
        try:
            payload: object = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return read_local_model(SETTINGS_PATH, GlobalSettings)

        if not isinstance(payload, dict):
            return read_local_model(SETTINGS_PATH, GlobalSettings)
        payload = cast(dict[str, object], payload)
        behaviors = payload.get("behaviors")
        if not isinstance(behaviors, dict) or "do_quest" not in behaviors:
            return read_local_model(SETTINGS_PATH, GlobalSettings)

        migrated_payload = dict(payload)
        migrated_behaviors = dict(cast(dict[str, object], behaviors))
        del migrated_behaviors["do_quest"]
        migrated_payload["behaviors"] = migrated_behaviors
        try:
            settings = GlobalSettings.model_validate(migrated_payload)
        except ValidationError as error:
            message = f"Invalid local file: {SETTINGS_PATH.name}. Fix it or restore a backup."
            raise RuntimeSetupError(message) from error
        self._save(settings)
        return settings

    def _save(self, settings: GlobalSettings) -> None:
        with acquire_file_lock(SETTINGS_PATH):
            atomic_write_text(SETTINGS_PATH, settings.model_dump_json(indent=2))
            self._settings = settings

    def sonji_api_key(self) -> str | None:
        key = self.get().sonji_api_key
        return (os.getenv("SONJI_API_KEY") if key is None else key) or None

    def update_behaviors(self, behaviors: BehaviorSettings, enabled: bool) -> None:
        with self._lock:
            current = self.get()
            self._save(
                current.model_copy(update={"behaviors": behaviors, "enable_account_automation": enabled})
            )

    def update_sonji_key(self, key: str | None) -> None:
        with self._lock:
            self._save(self.get().model_copy(update={"sonji_api_key": key}))
