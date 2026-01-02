from datetime import datetime
from pathlib import Path

from base_python.singleton import Singleton
from filelock import FileLock
from pydantic import BaseModel, Field

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.atomic_file import acquire_file_lock
from src.consts import RESOURCE_FOLDER


class PlayerInfoSnapshot(BaseModel):
    updated_at: datetime
    character_id: int
    character_name: str
    breed_id: int
    level: int
    kamas: int
    server_id: int
    job_levels_by_id: dict[int, int]
    map_id: int
    has_guild: bool
    guild_chest_tab_number: int


class PlayerInfoFile(BaseModel):
    player_info_by_login: dict[str, PlayerInfoSnapshot] = Field(default_factory=dict[str, PlayerInfoSnapshot])


class PlayerInfoStorage(metaclass=Singleton):
    _FILE_PATH = Path(RESOURCE_FOLDER) / "bot_player_infos.json"
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _load(self) -> PlayerInfoFile:
        if not self._FILE_PATH.exists():
            return PlayerInfoFile()
        return PlayerInfoFile.model_validate_json(self._FILE_PATH.read_text(encoding="utf-8"))

    def _acquire_file_lock(self) -> FileLock:
        return acquire_file_lock(self._FILE_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS)

    def _save(self, player_info_file: PlayerInfoFile) -> None:
        self._FILE_PATH.write_text(player_info_file.model_dump_json(indent=2), encoding="utf-8")

    def get_snapshot(self, login: str) -> PlayerInfoSnapshot | None:
        with self._acquire_file_lock():
            return self._load().player_info_by_login.get(login)

    def save_snapshot(self, login: str, snapshot: PlayerInfoSnapshot) -> None:
        with self._acquire_file_lock():
            player_info_file = self._load()
            player_info_file.player_info_by_login[login] = snapshot
            self._save(player_info_file)

    def remove_snapshot(self, login: str) -> None:
        with self._acquire_file_lock():
            player_info_file = self._load()
            if login not in player_info_file.player_info_by_login:
                return
            del player_info_file.player_info_by_login[login]
            self._save(player_info_file)
