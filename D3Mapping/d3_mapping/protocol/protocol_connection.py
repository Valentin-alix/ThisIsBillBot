import datetime
import traceback
from typing import Any

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError, Message

from D3Mapping.d3_mapping.models.message import MessageInfo
from D3Mapping.d3_mapping.resources.protos.connection.login_message_pb2 import (
    Event,
    LoginMessage,
    Request,
    Response,
)


def get_conn_msg(content: bytes) -> tuple[Request | Response | Event, Message]:
    msg = LoginMessage()
    msg.ParseFromString(content)

    msg_type: str = msg.WhichOneof("content")
    msg_content: Request | Response | Event = getattr(msg, msg_type)

    sub_msg_type: str = msg_content.WhichOneof("content")
    sub_msg_content: Message = getattr(msg_content, sub_msg_type)

    return msg_content, sub_msg_content


def get_conn_msg_info(
    content: bytes, sub_msg: Message, from_server: bool
) -> MessageInfo:
    received_msg_time = datetime.datetime.now()
    msg_json: dict[str, Any] = {}
    sub_msg_name: str = ""
    try:
        sub_msg_name = sub_msg.__class__.__name__
        msg_json = MessageToDict(sub_msg)
    except (DecodeError, TypeError):
        print(traceback.format_exc())

    return MessageInfo(
        received_time=received_msg_time,
        from_server=from_server,
        msg_json=msg_json,
        sub_msg_name=sub_msg_name,
        obf_msg_json=None,
    )
