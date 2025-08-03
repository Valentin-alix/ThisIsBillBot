from collections.abc import Callable

from ankama_launcher_emulator_premium.installation.cytrus import (
    check_cytrus_installation,
)
from ankama_launcher_emulator_premium.utils.environment import (
    RETRO_PATH,
    RETRO_RELEASE_JSON_PATH,
)


def check_retro_installation(
    on_progress: Callable[[str], None] | None = None,
) -> None:
    check_cytrus_installation(
        game="retro",
        release="main",
        exe_path=RETRO_PATH,
        release_json_path=RETRO_RELEASE_JSON_PATH,
        log_prefix="RETRO",
        on_progress=on_progress,
    )
