import datetime
import json
import traceback
from typing import cast

from google.protobuf import descriptor_pool
from google.protobuf.descriptor import Descriptor
from google.protobuf.internal.decoder import _DecodeVarint  # type: ignore
from google.protobuf.internal.encoder import _EncodeVarint  # type: ignore
from google.protobuf.json_format import MessageToDict, MessageToJson
from google.protobuf.message import DecodeError, Message
from google.protobuf.message_factory import GetMessageClass

from db_dofus_unity.consts import (
    PROTO_ROOT_PATH,
    MAPPING_CONN_PROTO_PATH,
    MAPPING_GAME_PROTO_PATH,
)
from db_dofus_unity.protos.connection.login_message_pb2 import LoginMessage
from db_dofus_unity.protos.game.game_message_pb2 import (
    Request,
    Response,
    Event,
    GameMessage,
)
from db_dofus_unity.protos.game.gamemap_pb2 import MapComplementaryInformationEvent
from src.consts import TYPE_URL_PREFIX
from src.interfaces.models.message import MessageInfo
from src.protocol.registry import import_and_get_all_msg_from_folder

import_and_get_all_msg_from_folder(PROTO_ROOT_PATH)

POOL: descriptor_pool.DescriptorPool = descriptor_pool.Default()

with open(MAPPING_CONN_PROTO_PATH, "rb") as file:
    MAPPING_CONN_PROTO_TO_REAL: dict[str, str] = json.load(file)

with open(MAPPING_GAME_PROTO_PATH, "rb") as file:
    MAPPING_GAME_PROTO_TO_REAL: dict[str, str] = json.load(file)
    MAPPING_GAME_PROTO_TO_OBF = {
        value: key for key, value in MAPPING_GAME_PROTO_TO_REAL.items()
    }


def decode_varint_size(data: bytes) -> tuple[int, int]:
    size, new_pos = _DecodeVarint(data, 0)
    return size, new_pos


def encode_varint(value: int) -> bytes:
    return _EncodeVarint(bytes, value)


def encode_msg(msg: Message) -> bytes:
    msg_content_datas = msg.SerializeToString()
    return encode_varint(len(msg_content_datas)) + msg_content_datas


def get_conn_msg_info(content: bytes) -> tuple[MessageInfo, Message | None]:
    received_msg_time = datetime.datetime.now()
    server_type = "CONN"

    msg_json: dict = {}
    msg_class_name: str = ""
    sub_msg_content: Message | None = None
    sub_msg_name: str = ""
    try:
        msg = LoginMessage()
        msg.ParseFromString(content)

        msg_content: Request | Response | Event
        if msg.HasField("request"):
            msg_class_name = "REQ"
            msg_content = msg.request
        elif msg.HasField("response"):
            msg_class_name = "RES"
            msg_content = msg.response
        else:
            msg_class_name = "EVT"
            msg_content = msg.event

        sub_msg_type: str = msg_content.WhichOneof("content")
        sub_msg_content = getattr(msg_content, sub_msg_type)
        sub_msg_name = sub_msg_content.__class__.__name__
        msg_json = MessageToDict(msg)
    except (DecodeError, TypeError):
        print(traceback.format_exc())

    return (
        MessageInfo(
            received_time=received_msg_time,
            server_type=server_type,
            msg_json=msg_json,
            msg_name=msg_class_name,
            sub_msg_name=sub_msg_name,
            raw_content=content,
        ),
        sub_msg_content,
    )


def get_game_msg_info(content: bytes) -> tuple[MessageInfo, Message | None]:
    received_msg_time = datetime.datetime.now()
    server_type = "GAME"

    msg_json: dict = {}
    msg_class_name: str = ""
    type_url_name: str = ""
    sub_msg_content: Message | None = None
    try:
        msg = GameMessage()
        msg.ParseFromString(content)

        msg_content: Request | Response | Event
        if msg.HasField("request"):
            msg_class_name = "REQ"
            msg_content = msg.request
        elif msg.HasField("response"):
            msg_class_name = "RES"
            msg_content = msg.response
        else:
            msg_class_name = "EVT"
            msg_content = msg.event

        short_obfuscated_type_url = msg_content.content.type_url.split("/")[-1]
        short_readable_type_url = MAPPING_GAME_PROTO_TO_REAL.get(
            short_obfuscated_type_url
        )
        if short_readable_type_url:
            # put readable msg as type url
            msg_content.content.type_url = TYPE_URL_PREFIX + short_readable_type_url

            type_url_name = f"{short_obfuscated_type_url} ⭢ {short_readable_type_url.split(".")[-1]}"

            msg_json = MessageToDict(msg)
            sub_msg_descriptor: Descriptor = POOL.FindMessageTypeByName(
                short_readable_type_url
            )
            sub_msg_type = GetMessageClass(sub_msg_descriptor)
            sub_msg_content = sub_msg_type()
            msg_content.content.Unpack(sub_msg_content)
        else:
            type_url_name = f"{short_obfuscated_type_url} ⭢ ???"

    except (DecodeError, TypeError):
        print(traceback.format_exc())

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


if __name__ == "__main__":
    content = b'\x1a\x97\x05\n\x94\x05\n\x13type.ankama.com/hyc\x12\xfc\x04\x08_\x10\x81\x88\x80Z"g\x08\x8a\x87\xd4\xcd\x05\x12\x03\x10\xc2\x02\x1aZ\n%\x08\x01\x12\x03y\x94\x11\x1a\x18\xa6\x83\xb3\x0e\xb0\xa8\xc5\x12\xb3\xc2\xdc\x1c\xb3\xc2\xdc$\x94\x89\xf7.\xb3\xc2\xdc4"\x02\xa0\x01\x121"/\n\rVacolat-Angor\x12\x1e\n\x01\x0b\x10\x01\x1a\x02X\x01 \xa7\xb5\xb4V*\x0e\x08\x02 \x90\x87\xd4\xcd\x05(\x90\x87\xd4\xcd\x05"F\x08\xe0\xe3\xfe\xff\xff\xff\xff\xff\xff\x01\x12\x05\x10\xe3\x03\x18\x03\x1a2\n)\x08\x01\x12\x07F\xbc\x10\x94\x02\xb3\x0b\x1a\x18\xb7\xe2\xad\r\x96\xf8\xe8\x13\xca\xda\x9a\x1d\xb2\xc6\xba$\xcd\xa8\x91+\x91\x8e\xa13"\x02\x82\x01\x12\x05:\x03\x08\xd7\x04"4\x08\xde\xe3\xfe\xff\xff\xff\xff\xff\xff\x01\x12\x04\x10\'\x18\x05\x1a!\n\x03\x08\xfa\x04\x12\x1a2\x18\n\t\n\x07\x08\xe9\x03\x10\x01\x18\x0b\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x18\x01"Q\x08\xdd\xe3\xfe\xff\xff\xff\xff\xff\xff\x01\x12\x05\x10\x98\x01\x18\x05\x1a=\n\x03\x08\xfd\x04\x12624\n%\n\x07\x08\xed\x03\x10\x01\x18\x0b\x12\x0c\x08\xec\x03\x10\x02\x18\x0c"\x03\x08\xfc\x04\x12\x0c\x08\xeb\x03\x10\x03\x18\r"\x03\x08\xae\x03\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x18\x01"\x89\x01\x08\xdc\xe3\xfe\xff\xff\xff\xff\xff\xff\x01\x12\x05\x10\xe5\x01\x18\x07\x1au\n\x03\x08\xfa\x04\x12n2l\n]\n\x07\x08\xe9\x03\x10\x01\x18\x0b\x12\x0c\x08\xea\x03\x10\x03\x18\r"\x03\x08\xfb\x04\x12\x0c\x08\xeb\x03\x10\x03\x18\r"\x03\x08\xae\x03\x12\x0c\x08\xeb\x03\x10\x05\x18\x0f"\x03\x08\xae\x03\x12\x0c\x08\xeb\x03\x10\x02\x18\x0c"\x03\x08\xae\x03\x12\x0c\x08\xea\x03\x10\x05\x18\x0f"\x03\x08\xfb\x04\x12\x0c\x08\xec\x03\x10\x05\x18\x0f"\x03\x08\xfc\x04\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x18\x01*$\x08\xf6\xbb\x1f\x10\xbc\x02\x1a\x07\x08\xe9\x02\x10\xd7\xae\x01\x1a\x07\x08\xd3\x02\x10\xd8\xae\x01\x1a\x07\x08\xb8\x01\x10\xd6\xae\x01(\x01*\x1a\x08\xa4\xbf\x1f\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x1a\x07\x08\xb8\x01\x10\xd5\xae\x01(\x01*\x10\x08\xdb\xb4\x1f\x10\x01\x1a\x06\x08\x06\x10\xb8\x94\x010\x01*\x11\x08\xdc\xb4\x1f\x10\x1f"\x06\x08%\x10\xba\x94\x010\xc8\x01*\x11\x08\xa7\xb7\x1f\x10\xfe\x01\x1a\x06\x08D\x10\xe9\xae\x010\x01*\x0f\x08\x89\xb7\x1f\x10K\x1a\x05\x08|\x10\xe6c0\x012\x07\x08\xdb\xb4\x1f\x10\xfb\x022\x07\x08\xdc\xb4\x1f\x10\xe1\x032\x06\x08\xa7\xb7\x1f\x10Q2\x06\x08\x89\xb7\x1f\x10OH\x01'

    msg_info, msg = get_game_msg_info(content)
    print(msg_info)
    print(MessageToJson(msg))
    msg = cast(MapComplementaryInformationEvent, msg)
    print(msg.map_id)
