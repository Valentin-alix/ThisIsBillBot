import datetime
from dataclasses import dataclass
from typing import Any


@dataclass
class MessageInfo:
    received_time: datetime.datetime
    server_type: str
    msg_json: dict[str, Any]
    msg_name: str
    sub_msg_name: str
    raw_content: bytes
