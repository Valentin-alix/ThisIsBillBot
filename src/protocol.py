import importlib
from google.protobuf.internal.decoder import _DecodeVarint  # type: ignore
from google.protobuf import message as _message

PREFIX = "type.ankama.com/"


def decode_varint_size(data: bytes) -> tuple[int, int]:
    size, new_pos = _DecodeVarint(data, 0)
    return size, new_pos


def load_message_type_from_type_url(type_url: str) -> type[_message.Message]:
    msg_name = type_url.split(PREFIX)[1]

    module_path = msg_name.rsplit(".", 1)[0] + "_pb2"
    class_name = msg_name.rsplit(".", 1)[1]

    module = importlib.import_module(module_path)
    message_class = getattr(module, class_name)
    return message_class
