from threading import RLock

from utils.singleton import Singleton

from ankama_launcher_emulator.consts import SCHEDULE_PROFILES_PATH
from ankama_launcher_emulator.interfaces.schedule_profile import (
    ScheduleProfile,
    ScheduleProfiles,
)


class ScheduleProfileController(metaclass=Singleton):
    _LOCK = RLock()

    def get_all_profiles(self) -> dict[str, ScheduleProfile]:
        with self._LOCK:
            return ScheduleProfiles.model_validate_json(
                SCHEDULE_PROFILES_PATH.read_text(encoding="utf-8")
            ).profiles

    def get_profile(self, profile_id: str) -> ScheduleProfile | None:
        return self.get_all_profiles().get(profile_id)
