import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))


from ankama_launcher_emulator.consts import ASAR_PATH, RESOURCES

if __name__ == "__main__":
    print(
        "asar",
        "extract",
        f'"{str(ASAR_PATH)}"'.replace("\\", "/"),
        f'"{str(Path(RESOURCES) / "launcher_decompiled")}"'.replace("\\", "/"),
    )
    subprocess.run(
        [
            "asar.cmd",
            "extract",
            str(ASAR_PATH),
            str(Path(RESOURCES) / "launcher_decompiled"),
        ],
        check=False,
    )
