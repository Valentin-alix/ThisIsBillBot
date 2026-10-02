import sys


def require_windows() -> None:
    if sys.platform != "win32":
        raise RuntimeError("This program requires Windows.")
