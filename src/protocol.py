import datetime
import json
import traceback

from google.protobuf.any_pb2 import Any
from google.protobuf.internal.decoder import _DecodeVarint  # type: ignore
from google.protobuf.internal.encoder import _EncodeVarint  # type: ignore
from google.protobuf.json_format import MessageToJson
from google.protobuf.message import DecodeError, Message

from com.ankama.dofus.server.connection.protocol_pb2 import Message as ConnectionMessage
from com.ankama.dofus.server.game.protocol_pb2 import Message as GameMessage
from src.consts import PROTO_ROOT_PATH
from src.enums import ServerType
from src.models.message_info import MessageInfo
from src.utils import import_all_classes_from_folder

import_all_classes_from_folder(PROTO_ROOT_PATH)


def decode_varint_size(data: bytes) -> tuple[int, int]:
    size, new_pos = _DecodeVarint(data, 0)
    return size, new_pos


def encode_varint(value: int) -> bytes:
    return _EncodeVarint(bytes, value)


def encode_msg(msg: Message) -> bytes:
    msg_content_datas = msg.SerializeToString()
    return encode_varint(len(msg_content_datas)) + msg_content_datas


def decode_msg(msg: Message, content: bytes) -> None:
    try:
        msg.ParseFromString(content)
    except DecodeError:
        print(traceback.format_exc())


def get_conn_msg_info(msg: ConnectionMessage) -> MessageInfo:
    received_msg_time = datetime.datetime.now()
    server_type = ServerType.CONNECTION
    msg_json = MessageToJson(msg)

    msg_type = msg.WhichOneof("content") or ""
    msg_content = getattr(msg, msg_type, None)

    if msg_content and (msg_content_type := msg_content.WhichOneof("content")):
        msg_content_type = getattr(msg_content, msg_content_type).__class__.__name__
    else:
        msg_content_type = ""

    return MessageInfo(
        received_time=received_msg_time,
        server_type=server_type,
        msg_json=json.loads(msg_json),
        msg_type=msg_type,
        msg_content_type=msg_content_type,
    )


def get_game_msg_info(msg: GameMessage) -> MessageInfo:
    received_msg_time = datetime.datetime.now()
    server_type = ServerType.GAME
    try:
        msg_json = json.loads(MessageToJson(msg))
    except DecodeError:
        msg_json = {}
        print(traceback.format_exc())

    msg_type_field = msg.WhichOneof("content") or ""
    msg_content = getattr(msg, msg_type_field, None)

    if msg_content:
        sub_msg_content: Any = msg_content.content
        type_sub_msg_content = sub_msg_content.TypeName().split(".")[-1]
    else:
        type_sub_msg_content = ""

    return MessageInfo(
        received_time=received_msg_time,
        server_type=server_type,
        msg_json=msg_json,
        msg_type=msg_type_field,
        msg_content_type=type_sub_msg_content,
    )
