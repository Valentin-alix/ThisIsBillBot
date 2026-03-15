from utils.local_json import read_local_model
from threading import RLock
import re

from utils.singleton import Singleton

from ankama_launcher_emulator.consts import SCHEDULE_PROFILES_PATH
from ankama_launcher_emulator.controller.proxy import ProxyController
from ankama_launcher_emulator.utils.atomic_file import acquire_file_lock, atomic_write_text
from ankama_launcher_emulator.interfaces.schedule_profile import (
    ScheduleProfile,
    ScheduleProfiles,
    SCHEDULE_RANDOM_MINUTES_MAX,
)


class ScheduleProfileController(metaclass=Singleton):
    _LOCK = RLock()

    def get_all_profiles(self) -> dict[str, ScheduleProfile]:
        with self._LOCK:
            if not SCHEDULE_PROFILES_PATH.exists():
                return {}
            return read_local_model(SCHEDULE_PROFILES_PATH, ScheduleProfiles).profiles

    def get_profile(self, profile_id: str) -> ScheduleProfile | None:
        return self.get_all_profiles().get(profile_id)

    def remove_profile(self, profile_id: str) -> None:
        with self._LOCK, acquire_file_lock(SCHEDULE_PROFILES_PATH):
            profiles = self.get_all_profiles()
            if profiles.pop(profile_id, None) is not None:
                atomic_write_text(SCHEDULE_PROFILES_PATH, ScheduleProfiles(profiles=profiles).model_dump_json(indent=2))

    def save_profile(self, profile_id: str, profile: ScheduleProfile, *, create: bool = False) -> None:
        if not profile_id.strip() or not profile.name_fr.strip():
            raise ValueError("Schedule identifier and name are required.")
        ProxyController().get_proxy(profile.proxy_id)
        occupied: set[int] = set()
        for day, slots in profile.slots_by_day.items():
            if day not in {str(index) for index in range(7)}:
                raise ValueError("Invalid schedule day.")
            for slot in slots:
                if not all(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value) for value in (slot.start, slot.end)):
                    raise ValueError("Times must use the HH:MM format.")
                start, end = (int(value[:2]) * 60 + int(value[3:]) for value in (slot.start, slot.end))
                duration = (end - start) % 1440
                if duration <= 2 * SCHEDULE_RANDOM_MINUTES_MAX:
                    raise ValueError("Each time slot must exceed one hour to preserve scheduling margins.")
                minutes = {(int(day) * 1440 + start + offset) % 10080 for offset in range(duration)}
                if occupied & minutes:
                    raise ValueError("Schedule time slots overlap.")
                occupied.update(minutes)
        with self._LOCK, acquire_file_lock(SCHEDULE_PROFILES_PATH):
            profiles = self.get_all_profiles()
            if create and profile_id in profiles:
                raise ValueError("This schedule identifier already exists.")
            if not create and profile_id not in profiles:
                raise ValueError("This schedule no longer exists. Refresh the list.")
            profiles[profile_id] = profile
            atomic_write_text(SCHEDULE_PROFILES_PATH, ScheduleProfiles(profiles=profiles).model_dump_json(indent=2))
