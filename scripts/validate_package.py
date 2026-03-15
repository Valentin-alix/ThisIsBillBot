import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
from ctypes import wintypes
from pathlib import Path


def close_window(pid: int) -> None:
    user32 = ctypes.windll.user32
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

    def visit(hwnd: int, _: int) -> bool:
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid:
            user32.PostMessageW(hwnd, 0x0010, 0, 0)
        return True

    user32.EnumWindows(callback_type(visit), 0)


def validate_package(folder: Path) -> None:
    version = folder / "_internal/VERSION"
    if not version.is_file():
        raise RuntimeError("Packaged VERSION file is missing")
    with tempfile.TemporaryDirectory(prefix="bot-package-") as temporary:
        root = Path(temporary)
        package = root / "release"
        shutil.copytree(folder, package)
        profile = root / "profile"
        environment = dict(os.environ)
        environment.update(
            USERPROFILE=str(profile),
            APPDATA=str(profile / "AppData/Roaming"),
            LOCALAPPDATA=str(profile / "AppData/Local"),
            DEBUG="0",
            PYTHON_DOTENV_DISABLED="1",
            PLAYWRIGHT_BROWSERS_PATH=str(root / "absent-browser-cache"),
        )
        for name in (
            "OBF_GAME_DIR",
            "NON_OBF_GAME_DIR",
            "PROTOC_PATH",
            "IDA_EXE",
            "OPENAI_API_KEY",
            "SONJI_API_KEY",
        ):
            environment.pop(name, None)
        log_path = profile / "AppData/Local/Bot-DofusUnity/resources/diagnostics.log"
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        process = subprocess.Popen(
            [str(package / "Bot-DofusUnity.exe"), "--no-auto"],
            cwd=root,
            env=environment,
            startupinfo=startup,
        )
        try:
            deadline = time.monotonic() + 120
            log = ""
            while time.monotonic() < deadline:
                log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
                if "The installed Dofus version is missing or unreadable." in log:
                    break
                if process.poll() is not None or "ERROR" in log:
                    raise RuntimeError(f"Packaged startup failed:\n{log}")
                time.sleep(0.2)
            else:
                raise TimeoutError(f"Packaged startup did not finish:\n{log}")
            close_window(process.pid)
            if process.wait(timeout=30) != 1:
                raise RuntimeError("Packaged startup must refuse an installation without Dofus")
            if "Application ready." in log:
                raise RuntimeError("GUI started despite missing Dofus")
            print("PASS: bundled VERSION file, missing-game startup refusal and exit code 1")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()


if __name__ == "__main__":
    validate_package(Path(sys.argv[1]).resolve())
