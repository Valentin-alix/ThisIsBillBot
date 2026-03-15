from collections.abc import Callable

from ankama_launcher_emulator.installation.cytrus import (
    check_cytrus_installation,
)
from ankama_launcher_emulator.utils.environment import (
    resolve_dofus_path,
    RELEASE_JSON_PATH,
)


def check_dofus3_installation(
    on_progress: Callable[[str], None] | None = None,
) -> None:
    check_cytrus_installation(
        game="dofus",
        release="dofus3",
        exe_path=resolve_dofus_path(),
        release_json_path=RELEASE_JSON_PATH,
        log_prefix="DOFUS3",
        on_progress=on_progress,
    )
