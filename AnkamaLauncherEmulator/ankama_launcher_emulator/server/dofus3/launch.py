import logging
import os
from contextlib import ExitStack

import frida

from ankama_launcher_emulator.consts import LAUNCHER_PORT
from ankama_launcher_emulator.interfaces.game import GameNameEnum
from ankama_launcher_emulator.utils.environment import resolve_dofus_path, ZAAP_PATH
from src.services.install_validation import check_resource
from src.utils.project_paths import FRIDA_SCRIPT_PATH

logger = logging.getLogger()


def launch_dofus_exe(
    instance_id: int,
    random_hash: str,
    connection_port: int,
) -> int:
    log_path = os.path.join(ZAAP_PATH, "gamesLogs", "dofus-dofus3", "dofus.log")

    command: list[str | bytes] = [
        resolve_dofus_path(),
        "--port",
        str(LAUNCHER_PORT),
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
        "ZAAP_PORT": str(LAUNCHER_PORT),
        "ZAAP_RELEASE": "dofus3",
    }

    check_resource(FRIDA_SCRIPT_PATH)
    device = frida.get_local_device()
    pid = device.spawn(program=command, env=env)

    with ExitStack() as cleanup:
        cleanup.callback(device.kill, pid)
        load_frida_script(pid, connection_port, device=device, resume=True)
        cleanup.pop_all()

    return pid


def load_frida_script(
    pid: int,
    port: int,
    device: frida.Device,
    resume: bool = False,
) -> None:
    session = device.attach(pid)
    script = session.create_script(FRIDA_SCRIPT_PATH.read_text(encoding="utf-8"))
    script.load()
    script.post({"port": port, "proxyIp": [127, 0, 0, 1]})
    if resume:
        device.resume(pid)
