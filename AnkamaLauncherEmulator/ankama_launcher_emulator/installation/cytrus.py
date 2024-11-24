import json
import logging
import os
import platform
import subprocess
from typing import Callable, Literal

from ankama_launcher_emulator.consts import ANSI_ESCAPE, CYTRUS_INSTALLED

logger = logging.getLogger()

Game = Literal["dofus"] | Literal["retro"]
Release = Literal["dofus3"] | Literal["main"]


def cytrus_get_latest_version(game: Game, release: Release) -> str:
    result = subprocess.run(
        [
            "cytrus-v6",
            "version",
            "--game",
            game,
            "--release",
            release,
            "--platform",
            platform.system().lower(),
        ],
        capture_output=True,
        text=True,
        check=True,
        shell=True,
    )
    return result.stdout.strip()


def cytrus_download(
    game: Game,
    release: Release,
    version: str,
    output_dir: str,
    log_prefix: str,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    process = subprocess.Popen(
        [
            "cytrus-v6",
            "download",
            "--game",
            game,
            "--release",
            release,
            "--version",
            version,
            "--output",
            output_dir,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
    )
    if process.stdout:
        for line in process.stdout:
            line = ANSI_ESCAPE.sub("", line).rstrip()
            if line:
                logger.debug(f"[{log_prefix}] {line}")
                if on_progress:
                    on_progress(line)
    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, "cytrus-v6")


def check_cytrus_installation(
    game: Game,
    release: Release,
    exe_path: str,
    release_json_path: str,
    log_prefix: str,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    if not CYTRUS_INSTALLED:
        return logger.warning("Cytrus not installed, skipping auto update")
    latest_version = cytrus_get_latest_version(game, release)
    logger.info(f"[{log_prefix}] Latest cytrus version: {latest_version}")

    release_data: dict = {}
    local_version: str | None = None
    if os.path.exists(release_json_path):
        with open(release_json_path, "r") as file:
            release_data = json.load(file)
        local_version = release_data.get("version")

    if local_version != latest_version:
        game_dir = os.path.dirname(exe_path)
        logger.info(
            f"[{log_prefix}] Version mismatch (local={local_version}, latest={latest_version}), downloading..."
        )
        if on_progress:
            on_progress(
                f"Update available ({local_version or 'none'} → {latest_version}), downloading..."
            )
        cytrus_download(
            game, release, latest_version, game_dir, log_prefix, on_progress
        )
        logger.info(f"[{log_prefix}] Download complete.")
        release_data["version"] = latest_version
        os.makedirs(os.path.dirname(release_json_path), exist_ok=True)
        with open(release_json_path, "w") as file:
            json.dump(release_data, file, indent=2)
