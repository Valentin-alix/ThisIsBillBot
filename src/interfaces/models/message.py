import datetime
from dataclasses import dataclass


@dataclass
class MessageInfo:
    received_time: datetime.datetime
    server_type: str
    msg_json: dict
    msg_name: str
    sub_msg_name: str
    raw_content: bytes
