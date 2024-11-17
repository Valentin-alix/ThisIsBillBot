import datetime
from typing import Any

from src.utils.dataclass_utils import AppModel


class MessageInfo(AppModel):
    received_time: datetime.datetime
    from_server: bool
    sub_msg_name: str
    obf_msg_json: dict[str, Any] | None = None
    msg_json: dict[str, Any] | None = None
