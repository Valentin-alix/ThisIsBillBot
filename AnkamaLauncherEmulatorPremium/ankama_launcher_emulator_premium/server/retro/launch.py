import logging
import os
import socket
from functools import cache
from pathlib import Path
from threading import Event

import frida

from ankama_launcher_emulator_premium.consts import LAUNCHER_PORT
from ankama_launcher_emulator_premium.interfaces.game import GameNameEnum
from ankama_launcher_emulator_premium.utils.environment import RETRO_PATH, ZAAP_PATH


@cache
def _retro_cdn_ips() -> list[str]:
    return socket.gethostbyname_ex("dofusretro.cdn.ankama.com")[2]


logger = logging.getLogger()


def launch_retro_exe(instance_id: int, random_hash: str, port: int) -> int:
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

    load_frida_script(pid, port, resume=True)

    return pid


def load_frida_script(pid: int, port: int, resume: bool = False) -> None:
    session = frida.attach(pid)
    with open(Path(__file__).parent / "script.js", encoding="utf-8") as script_file:
        script = session.create_script(script_file.read())

    hooks_ready = Event()

    def on_message(message: FridaMessage, _data: bytes | None) -> None:
        if message.get("type") == "send":
            payload = message["payload"]
            if payload == "hooks_ready":
                hooks_ready.set()
            elif isinstance(payload, int):
                child_pid = payload
                logger.info(f"Processus enfant détecté, injection Frida sur PID {child_pid}")
                load_frida_script(child_pid, port, resume=False)

    script.on("message", on_message)
    script.load()

    script.post({"retroCdn": _retro_cdn_ips(), "port": port, "proxyIp": [127, 0, 0, 1]})

    if resume:
        if not hooks_ready.wait(timeout=5.0):
            logger.warning("Frida hooks_ready timeout — resuming anyway")
        frida.resume(pid)


FridaMessage = dict[str, object]
