import os
from pathlib import Path
from src.utils.runtime_support import RuntimeSetupError


def get_bool_from_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    if raw.lower() in ("1", "true"):
        return True
    if raw.lower() in ("0", "false"):
        return False
    raise RuntimeSetupError(f"The {name} variable must be 0, 1, false, or true.")


def get_required_path(env_name: str) -> Path:
    raw_value = os.environ.get(env_name)
    if not raw_value:
        raise ValueError(f"Missing required path environment variable: {env_name}")
    return Path(raw_value).expanduser()


def get_optional_path(env_name: str, default: Path | None = None) -> Path | None:
    raw_value = os.environ.get(env_name)
    if not raw_value:
        return default
    return Path(raw_value).expanduser()


def get_path_from_env(env_name: str, default: Path) -> Path:
    raw_value = os.environ.get(env_name)
    if not raw_value:
        return default
    return Path(raw_value).expanduser()
