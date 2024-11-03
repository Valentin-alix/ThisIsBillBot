import datetime
from dataclasses import dataclass
from typing import Any


@dataclass
class MessageInfo:
    received_time: datetime.datetime
    from_server: bool
    sub_msg_name: str
    raw_content: bytes
    obf_msg_json: dict[str, Any] | None = None
    msg_json: dict[str, Any] | None = None
