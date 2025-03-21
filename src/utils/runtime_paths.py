import sys
from pathlib import Path

from src.protocol import _OBFUSCATED_PROTOS, _PROTO_CONN_PATH, _PROTO_GAME_PATH
from src.utils.registry import import_and_get_all_msg_from_folder


def add_import_path(path: Path) -> None:
    path_str = str(path)
    if path_str in sys.path:
        return
    sys.path.insert(0, path_str)


def configure_project_import_paths(project_root: Path) -> None:
    add_import_path(project_root)
    add_import_path(project_root / "DBDofusUnity")
    import_and_get_all_msg_from_folder(_OBFUSCATED_PROTOS)
    import_and_get_all_msg_from_folder(_PROTO_GAME_PATH)
    import_and_get_all_msg_from_folder(_PROTO_CONN_PATH)
