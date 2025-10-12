from src.protocol import _OBFUSCATED_PROTOS, _PROTO_CONN_PATH, _PROTO_GAME_PATH
from src.utils.registry import import_and_get_all_msg_from_folder


def configure_project_import_paths() -> None:
    import_and_get_all_msg_from_folder(_OBFUSCATED_PROTOS)
    import_and_get_all_msg_from_folder(_PROTO_GAME_PATH)
    import_and_get_all_msg_from_folder(_PROTO_CONN_PATH)
