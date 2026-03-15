from ankama_launcher_emulator.controller.bot_storage import BotStorageController
from ankama_launcher_emulator.controller.proxy import ProxyController
from ankama_launcher_emulator.controller.schedule_profile import ScheduleProfileController


def delete_schedule(profile_id: str) -> None:
    users = sorted(
        login for login, record in BotStorageController().get_all_records().items()
        if profile_id in (record.schedule_profile, record.quarantined_schedule_profile)
    )
    if users:
        raise ValueError("Schedule used by accounts: " + ", ".join(users) + ". Remove these assignments before deleting it.")
    ScheduleProfileController().remove_profile(profile_id)


def delete_proxy(proxy_id: str) -> None:
    users = sorted(
        identifier for identifier, profile in ScheduleProfileController().get_all_profiles().items()
        if profile.proxy_id == proxy_id
    )
    if users:
        raise ValueError("Proxy used by schedules: " + ", ".join(users) + ". Change their proxy before deleting it.")
    ProxyController().remove_config(proxy_id)
