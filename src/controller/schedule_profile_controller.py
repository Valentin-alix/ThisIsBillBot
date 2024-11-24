import json
import os
from threading import RLock

from pydantic import BaseModel

from src.const import RESOURCE_FOLDER
from src.utils.metaclasses.singleton import Singleton


class TimeSlot(BaseModel):
    start: str
    end: str


class ScheduleProfile(BaseModel):
    name_fr: str
    slots_by_day: dict[str, list[TimeSlot]]


class ScheduleProfiles(BaseModel):
    profiles: dict[str, ScheduleProfile]


class ScheduleProfileController(metaclass=Singleton):
    _PROFILES_LOCK = RLock()
    _PROFILES_PATH = os.path.join(RESOURCE_FOLDER, "schedule_profiles.json")

    def get_all_profiles(self) -> dict[str, ScheduleProfile]:
        with self._PROFILES_LOCK, open(self._PROFILES_PATH, "r") as file:
            data = ScheduleProfiles.model_validate(json.load(file))
            return data.profiles

    def get_profile(self, profile_id: str) -> ScheduleProfile | None:
        profiles = self.get_all_profiles()
        return profiles.get(profile_id)

    def get_profile_display_names(self) -> dict[str, str]:
        profiles = self.get_all_profiles()
        return {
            profile_id: f"{profile_id} - {profile.name_fr}"
            for profile_id, profile in profiles.items()
        }
