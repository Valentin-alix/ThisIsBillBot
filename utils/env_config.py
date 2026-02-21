import os
from pathlib import Path


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
