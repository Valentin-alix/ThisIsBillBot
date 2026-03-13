import sys
from pathlib import Path

IS_PACKAGED = getattr(sys, "frozen", False)
PROJECT_ROOT = Path(sys.executable).resolve().parent if IS_PACKAGED else Path(__file__).resolve().parent
BUNDLE_ROOT = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
USER_DATA_ROOT = Path.home() / "AppData" / "Local" / "Bot-DofusUnity" if IS_PACKAGED else PROJECT_ROOT
ENV_PATH = PROJECT_ROOT / ".env"


def ensure_packaged_runtime_data() -> None:
    if not IS_PACKAGED:
        return

    (USER_DATA_ROOT / "resources").mkdir(parents=True, exist_ok=True)
    launcher_resources = USER_DATA_ROOT / "AnkamaLauncherEmulator" / "resources"
    launcher_resources.mkdir(parents=True, exist_ok=True)
    schedule_profiles_path = launcher_resources / "schedule_profiles.json"
    if not schedule_profiles_path.exists():
        schedule_profiles_path.write_text('{"profiles": {}}\n', encoding="utf-8")
