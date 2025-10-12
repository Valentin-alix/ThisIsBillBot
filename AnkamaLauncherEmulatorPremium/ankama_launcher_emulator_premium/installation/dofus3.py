from collections.abc import Callable

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.installation.cytrus import (
    check_cytrus_installation,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.environment import (
    DOFUS_PATH,
    RELEASE_JSON_PATH,
)


def check_dofus3_installation(
    on_progress: Callable[[str], None] | None = None,
) -> None:
    check_cytrus_installation(
        game="dofus",
        release="dofus3",
        exe_path=DOFUS_PATH,
        release_json_path=RELEASE_JSON_PATH,
        log_prefix="DOFUS3",
        on_progress=on_progress,
    )
