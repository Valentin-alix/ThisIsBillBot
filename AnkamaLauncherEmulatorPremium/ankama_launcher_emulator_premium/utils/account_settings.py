from ankama_launcher_emulator_premium.interfaces.local_storage import (
    AppConfigEntry,
)
from ankama_launcher_emulator_premium.utils.bot_storage import BotStorageController


def load_account_settings(login: str) -> AppConfigEntry:
    """Return proxy settings saved for *login*, or defaults."""
    record = BotStorageController().get_record(login)
    return AppConfigEntry(proxy_url=record.proxy_url if record is not None else None)


def save_account_settings(login: str, proxy_url: str | None) -> None:
    """Persist the account-specific proxy URL in the bot store."""
    BotStorageController().update_record(
        login,
        lambda record: setattr(record, "proxy_url", proxy_url),
    )
