from datetime import datetime
from threading import RLock

from python_utils.cache import cache
from pydantic import BaseModel, RootModel

from src.const import HUMAN_SESSIONS_FILE


class MessageTimings(BaseModel):
    timestamp: float
    name: str


class MessageTimingsBySessionLogin(RootModel):
    root: dict[str, list[MessageTimings]]


SESSION_TIMINGS_LOCK = RLock()


class SessionTimingsController:
    def __init__(self, login: str) -> None:
        self.login = login
        self.pending_message_timings: list[MessageTimings] = []

    @staticmethod
    @cache
    def get_message_timings_by_session():
        with open(HUMAN_SESSIONS_FILE, "r") as file:
            return MessageTimingsBySessionLogin.model_validate_json(file.read()).root

    def add_message_timing(self, msg_name: str, msg_received_time: datetime):
        self.pending_message_timings.append(
            MessageTimings(name=msg_name, timestamp=msg_received_time.timestamp())
        )
        if len(self.pending_message_timings) > 10:
            self.insert_session_datas()

    def insert_session_datas(self):
        with SESSION_TIMINGS_LOCK, open(HUMAN_SESSIONS_FILE, "r+") as file:
            message_timings_by_session = (
                MessageTimingsBySessionLogin.model_validate_json(file.read())
            )
            message_timing_on_current = message_timings_by_session.root.get(
                self.login, []
            )
            message_timing_on_current.extend(self.pending_message_timings)
            message_timings_by_session.root[self.login] = message_timing_on_current
            self.pending_message_timings.clear()
            file.seek(0)
            file.write(message_timings_by_session.model_dump_json())
            file.truncate()
