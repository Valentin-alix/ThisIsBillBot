import datetime
import json
import traceback
from typing import Any

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message, DecodeError

from consts import MAPPING_CONN_PROTO_PATH
from protos.connection.login_message_pb2 import LoginMessage
from protos.connection.login_message_pb2 import Request, Response, Event
from src.interfaces.models.message import MessageInfo

with open(MAPPING_CONN_PROTO_PATH, "rb") as file:
    MAPPING_CONN_PROTO_TO_REAL: dict[str, str] = json.load(file)


def get_conn_msg(content: bytes) -> tuple[Request | Response | Event, Message]:
    msg = LoginMessage()
    msg.ParseFromString(content)

    msg_type: str = msg.WhichOneof("content")
    msg_content: Request | Response | Event = getattr(msg, msg_type)

    sub_msg_type: str = msg_content.WhichOneof("content")
    sub_msg_content: Message = getattr(msg_content, sub_msg_type)

    return msg_content, sub_msg_content


def get_conn_msg_info(content: bytes) -> tuple[MessageInfo, Message | None]:
    received_msg_time = datetime.datetime.now()
    server_type = "CONN"
    msg_json: dict[str, Any] = {}
    msg_class_name: str = ""
    sub_msg_content: Message | None = None
    sub_msg_name: str = ""

    try:
        msg_content, sub_msg_content = get_conn_msg(content)
        msg_class_name = msg_content.__class__.__name__
        sub_msg_name = sub_msg_content.__class__.__name__
        msg_json = MessageToDict(sub_msg_content)
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
