import logging
import os
from pathlib import Path

import frida

from ankama_launcher_emulator.consts import DOFUS_PATH, ZAAP_PATH
from ankama_launcher_emulator.interfaces.game_name_enum import GameNameEnum

logger = logging.getLogger()


def launch_dofus_exe(instance_id: int, random_hash: str, connection_port: int, interface_ip: str | None = None) -> int:
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

    pid = frida.spawn(program=command, env=env)

    load_frida_script(pid, connection_port, interface_ip=interface_ip, resume=True)

    return pid


def load_frida_script(pid: int, port: int, interface_ip: str | None = None, resume: bool = False):
    hook_path = Path(__file__).parent / "script.js"
    session = frida.attach(pid)
    script = session.create_script(hook_path.read_text(encoding="utf-8"))
    script.load()
    proxy_ip = [int(part) for part in interface_ip.split(".")] if interface_ip else [127, 0, 0, 1]
    script.post({"port": port, "proxyIp": proxy_ip})
    if resume:
        frida.resume(pid)
