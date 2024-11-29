import sys
from pathlib import Path


def add_import_path(path: Path) -> None:
    path_str = str(path)
    if path_str in sys.path:
        return
    sys.path.insert(0, path_str)


def configure_project_import_paths(project_root: Path) -> None:
    add_import_path(project_root)
    add_import_path(project_root / "DBDofusUnity")
