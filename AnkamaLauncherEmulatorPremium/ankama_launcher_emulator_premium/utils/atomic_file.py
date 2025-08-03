import os
import tempfile
from pathlib import Path

from filelock import FileLock


def atomic_write_text(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding=encoding,
        dir=path.parent,
        prefix=f"{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary_handle:
        temporary_path = Path(temporary_handle.name)
        temporary_handle.write(content)
        temporary_handle.flush()
        os.fsync(temporary_handle.fileno())
    try:
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def acquire_file_lock(path: Path, *, timeout_seconds: float = 20.0) -> FileLock:
    path.parent.mkdir(parents=True, exist_ok=True)
    return FileLock(Path(f"{path}.lock"), timeout=timeout_seconds)
