from DBDofusUnity.consts import PROTOS_ROOT
from src.utils.registry import import_and_get_all_msg_from_folder

_OBFUSCATED_PROTOS = str(PROTOS_ROOT / "obf" / "game")
_PROTO_GAME_PATH = str(PROTOS_ROOT / "non_obf" / "game")
_PROTO_CONN_PATH = str(PROTOS_ROOT / "non_obf" / "connection")


import_and_get_all_msg_from_folder(_OBFUSCATED_PROTOS)
import_and_get_all_msg_from_folder(_PROTO_GAME_PATH)
import_and_get_all_msg_from_folder(_PROTO_CONN_PATH)
