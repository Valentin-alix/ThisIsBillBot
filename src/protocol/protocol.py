import datetime
import json

from google.protobuf import descriptor_pool
from google.protobuf.descriptor import Descriptor
from google.protobuf.internal.decoder import _DecodeVarint  # type: ignore
from google.protobuf.internal.encoder import _EncodeVarint  # type: ignore
from google.protobuf.json_format import MessageToJson
from google.protobuf.message import DecodeError, Message
from google.protobuf.message_factory import GetMessageClass

from com.ankama.dofus.server.connection.protocol_pb2 import Message as ConnectionMessage
from com.ankama.dofus.server.game.protocol_pb2 import (
    Message as GameMessage,
    Request,
    Event,
    Response,
)
from src.consts import PROTO_ROOT_PATH

from src.interfaces.models.message_info import MessageInfo
from src.protocol.registry import import_and_get_all_msg_from_folder

import_and_get_all_msg_from_folder(PROTO_ROOT_PATH)


POOL: descriptor_pool.DescriptorPool = descriptor_pool.Default()


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
        print(f"error while decoding {msg.__class__.__name__}")


def get_conn_msg_info(msg: ConnectionMessage) -> tuple[MessageInfo, Message]:
    received_msg_time = datetime.datetime.now()
    server_type = "Connection"
    msg_json = MessageToJson(msg)

    msg_type: str = msg.WhichOneof("content")
    msg_content: Message = getattr(msg, msg_type)
    msg_class_name = msg_content.__class__.__name__

    sub_msg_type: str = msg_content.WhichOneof("content")
    sub_msg_content: Message = getattr(msg_content, sub_msg_type)
    sub_msg_class_name = sub_msg_content.__class__.__name__

    return MessageInfo(
        received_time=received_msg_time,
        server_type=server_type,
        msg_json=json.loads(msg_json),
        msg_name=msg_class_name,
        sub_msg_name=sub_msg_class_name,
    ), sub_msg_content


def get_game_msg_info(msg: GameMessage) -> tuple[MessageInfo, Message | None]:
    received_msg_time = datetime.datetime.now()
    server_type = "Game"
    try:
        msg_json = json.loads(MessageToJson(msg))
    except DecodeError:
        print("error while decoding")
        msg_json = {}

    msg_type: str = msg.WhichOneof("content")
    msg_content: Request | Response | Event = getattr(msg, msg_type)
    msg_class_name = msg_content.__class__.__name__

    sub_msg_descriptor: Descriptor = POOL.FindMessageTypeByName(
        msg_content.content.type_url.split("/")[-1]
    )
    sub_msg_type = GetMessageClass(sub_msg_descriptor)
    sub_msg_content = sub_msg_type()
    msg_content.content.Unpack(sub_msg_content)

    return MessageInfo(
        received_time=received_msg_time,
        server_type=server_type,
        msg_json=msg_json,
        msg_name=msg_class_name,
        sub_msg_name=sub_msg_type.__name__,
    ), sub_msg_content
