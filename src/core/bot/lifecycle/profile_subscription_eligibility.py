from dataclasses import dataclass

from ankama_launcher_emulator.controller.bot_storage import (
    BotStorageController,
)
from src.consts import (
    MAX_BOTS_PER_SCHEDULE_PROFILE,
    SUBSCRIPTION_MIN_KAMAS,
    SUBSCRIPTION_MIN_LEVEL,
)
from src.controller.player_info_storage import PlayerInfoStorage


@dataclass
class ProfileSubscriptionEligibility:
    def is_eligible(
        self,
        profile_id: str,
        current_login: str,
        current_level: int,
        current_kamas: int,
    ) -> bool:
        logins = [
            login
            for login, record in BotStorageController().get_all_records().items()
            if record.schedule_profile == profile_id
        ]
        if len(logins) != MAX_BOTS_PER_SCHEDULE_PROFILE:
            return False
        for login in logins:
            if login == current_login:
                if not self._meets_progression_requirements(current_level, current_kamas):
                    return False
                continue
            snapshot = PlayerInfoStorage().get_snapshot(login)
            if snapshot is None or not self._meets_progression_requirements(
                snapshot.level, snapshot.kamas
            ):
                return False
        return True

    @staticmethod
    def _meets_progression_requirements(level: int, kamas: int) -> bool:
        return level > SUBSCRIPTION_MIN_LEVEL and kamas >= SUBSCRIPTION_MIN_KAMAS
