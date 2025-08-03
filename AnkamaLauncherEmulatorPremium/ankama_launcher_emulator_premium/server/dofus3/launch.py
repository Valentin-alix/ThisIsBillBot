import logging
import os
from pathlib import Path

import frida
import frida.core

from ankama_launcher_emulator_premium.interfaces.game import GameNameEnum
from ankama_launcher_emulator_premium.utils.environment import DOFUS_PATH, ZAAP_PATH

logger = logging.getLogger()


def launch_dofus_exe(
    instance_id: int,
    random_hash: str,
    connection_port: int,
) -> int:
    log_path = os.path.join(ZAAP_PATH, "gamesLogs", "dofus-dofus3", "dofus.log")

    command: list[str | bytes] = [
        DOFUS_PATH,
        "--port",
        "26116",
        "--gameName",
        GameNameEnum.DOFUS.value,
        "--gameRelease",
        "dofus3",
        "--instanceId",
        str(instance_id),
        "--hash",
        random_hash,
        "--canLogin",
        "true",
        "-logFile",
        log_path,
        "--langCode",
        "fr",
        "--autoConnectType",
        "2",
        "--connectionPort",
        str(connection_port),
    ]

    env = {
        "ZAAP_CAN_AUTH": "true",
        "ZAAP_GAME": GameNameEnum.DOFUS.value,
        "ZAAP_HASH": random_hash,
        "ZAAP_INSTANCE_ID": str(instance_id),
        "ZAAP_LOGS_PATH": log_path,
        "ZAAP_PORT": "26116",
        "ZAAP_RELEASE": "dofus3",
    }

    device = frida.get_local_device()
    pid = device.spawn(program=command, env=env)

    load_frida_script(pid, connection_port, device=device, resume=True)

    return pid


def load_frida_script(
    pid: int,
    port: int,
    device: frida.core.Device,
    resume: bool = False,
) -> None:
    hook_path = Path(__file__).parent / "script.js"
    session = device.attach(pid)
    script = session.create_script(hook_path.read_text(encoding="utf-8"))
    script.load()
    script.post({"port": port, "proxyIp": [127, 0, 0, 1]})
    if resume:
        device.resume(pid)
