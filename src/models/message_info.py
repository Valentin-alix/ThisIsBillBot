import datetime
from dataclasses import dataclass

from src.enums import ServerType


@dataclass
class MessageInfo:
    received_time: datetime.datetime
    server_type: ServerType
    msg_json: dict
    msg_type: str
    msg_content_type: str
