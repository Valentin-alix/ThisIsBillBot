import datetime
import json
import traceback
from typing import Any

from google.protobuf import descriptor_pool
from google.protobuf.descriptor import Descriptor
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message, DecodeError
from google.protobuf.message_factory import GetMessageClass

from consts import (
    MAPPING_GAME_PROTO_PATH,
)
from protos.game.game_message_pb2 import Request, Response, Event, GameMessage
from src.const import TYPE_URL_PREFIX
from src.interfaces.models.message import MessageInfo

POOL: descriptor_pool.DescriptorPool = descriptor_pool.Default()

with open(MAPPING_GAME_PROTO_PATH, "rb") as file:
    MAPPING_GAME_PROTO_TO_REAL: dict[str, str] = json.load(file)
    MAPPING_GAME_PROTO_TO_OBF = {
        value: key for key, value in MAPPING_GAME_PROTO_TO_REAL.items()
    }


def get_game_msg(content: bytes) -> tuple[Request | Response | Event, Message | None]:
    msg = GameMessage()
    msg.ParseFromString(content)

    msg_type = msg.WhichOneof("content")
    msg_content: Request | Response | Event = getattr(msg, msg_type)

    short_obfuscated_type_url = msg_content.content.type_url.split("/")[-1]
    short_readable_type_url = MAPPING_GAME_PROTO_TO_REAL.get(short_obfuscated_type_url)
    if not short_readable_type_url:
        return msg_content, None

    # change type url for unpacking
    msg_content.content.type_url = TYPE_URL_PREFIX + short_readable_type_url
    sub_msg_descriptor: Descriptor = POOL.FindMessageTypeByName(short_readable_type_url)
    sub_msg_type = GetMessageClass(sub_msg_descriptor)
    sub_msg_content: Message = sub_msg_type()
    msg_content.content.Unpack(sub_msg_content)
    msg_content.content.type_url = TYPE_URL_PREFIX + short_obfuscated_type_url

    return msg_content, sub_msg_content


def get_game_msg_info(content: bytes) -> tuple[MessageInfo, Message | None]:
    received_msg_time = datetime.datetime.now()
    server_type = "GAME"

    msg_json: dict[str, Any] = {}
    msg_class_name: str = ""
    type_url_name: str = ""
    sub_msg_content: Message | None = None
    try:
        msg_content, sub_msg_content = get_game_msg(content)
        short_obfuscated_type_url = msg_content.content.type_url.split("/")[-1]
        msg_class_name = msg_content.__class__.__name__

        if sub_msg_content:
            msg_json = MessageToDict(sub_msg_content)
            short_readable_type_url = MAPPING_GAME_PROTO_TO_REAL[
                short_obfuscated_type_url
            ]
            type_url_name = f"{short_obfuscated_type_url} ⭢ {short_readable_type_url.split(".")[-1]}"
        else:
            type_url_name = f"{short_obfuscated_type_url} ⭢ ???"

    except (DecodeError, TypeError):
        print(f"{type_url_name} , {traceback.format_exc()}")

    return (
        MessageInfo(
            received_time=received_msg_time,
            server_type=server_type,
            msg_json=msg_json,
            msg_name=msg_class_name,
            sub_msg_name=type_url_name,
            raw_content=content,
        ),
        sub_msg_content,
    )
