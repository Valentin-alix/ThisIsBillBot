import json
import os

from ankama_launcher_emulator.consts import APP_CONFIG_PATH

_KEY = "account_proxy_interface"


def load_account_settings(login: str) -> tuple[str | None, str | None]:
    """Return (interface_ip, proxy_url) saved for *login*, or (None, None)."""
    if not os.path.exists(APP_CONFIG_PATH):
        return None, None
    try:
        with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
            config: dict = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None, None
    entry = config.get(_KEY, {}).get(login, {})
    return entry.get("interface_ip"), entry.get("proxy_url")


def save_account_settings(
    login: str, interface_ip: str | None, proxy_url: str | None
) -> None:
    """Persist interface_ip and proxy_url for *login* into APP_CONFIG_PATH."""
    if os.path.exists(APP_CONFIG_PATH):
        try:
            with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
                config: dict = json.load(f)
        except (json.JSONDecodeError, OSError):
            config = {}
    else:
        config = {}

    config.setdefault(_KEY, {})[login] = {
        "interface_ip": interface_ip,
        "proxy_url": proxy_url,
    }
    with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
