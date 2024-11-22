import json
import logging
import os
import socket
from pathlib import Path

import frida

from ankama_launcher_emulator.consts import LAUNCHER_PORT, RETRO_PATH, ZAAP_PATH
from ankama_launcher_emulator.interfaces.game_name_enum import GameNameEnum

RETRO_CDN = json.dumps(socket.gethostbyname_ex("dofusretro.cdn.ankama.com")[2])


logger = logging.getLogger()


def launch_retro_exe(
    instance_id: int, random_hash: str, port: int, interface_ip: str | None = None
) -> int:
    log_path = os.path.join(ZAAP_PATH, "gamesLogs", "retro")

    command: list[str | bytes] = [
        RETRO_PATH,
        f"--port={str(LAUNCHER_PORT)}",
        f"--gameName={GameNameEnum.RETRO.value}",
        "--gameRelease=main",
        f"--instanceId={str(instance_id)}",
        f"--gameInstanceKey={random_hash}",
    ]

    logger.info(command)

    env = {
        "ZAAP_CAN_AUTH": "true",
        "ZAAP_GAME": GameNameEnum.RETRO.value,
        "ZAAP_HASH": random_hash,
        "ZAAP_INSTANCE_ID": str(instance_id),
        "ZAAP_LOGS_PATH": log_path,
        "ZAAP_PORT": str(LAUNCHER_PORT),
        "ZAAP_RELEASE": "main",
    }

    pid = frida.spawn(program=command, env=env)

    load_frida_script(pid, port, interface_ip=interface_ip, resume=True)

    return pid


def load_frida_script(
    pid: int, port: int, interface_ip: str | None = None, resume: bool = False
):
    session = frida.attach(pid)
    script = session.create_script(open(Path(__file__).parent / "script.js").read())

    def on_message(message, _data):
        if message.get("type") == "send":
            child_pid = message["payload"]
            logger.info(
                f"Processus enfant détecté, injection Frida sur PID {child_pid}"
            )
            load_frida_script(child_pid, port, interface_ip=interface_ip, resume=False)

    script.on("message", on_message)
    script.load()

    proxy_ip = (
        [int(part) for part in interface_ip.split(".")]
        if interface_ip
        else [127, 0, 0, 1]
    )
    script.post({"retroCdn": json.loads(RETRO_CDN), "port": port, "proxyIp": proxy_ip})

    if resume:
        frida.resume(pid)
