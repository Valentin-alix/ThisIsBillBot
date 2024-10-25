import datetime
from dataclasses import dataclass
from typing import Any


@dataclass
class MessageInfo:
    received_time: datetime.datetime
    from_server: bool
    msg_json: dict[str, Any]
    sub_msg_name: str
    raw_content: bytes
