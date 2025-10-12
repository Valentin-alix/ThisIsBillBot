from threading import RLock

from base_python.singleton import Singleton

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import SCHEDULE_PROFILES_PATH
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.schedule_profile import (
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
