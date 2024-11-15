import base64
import io
import json
import os
import threading
from collections.abc import Iterator
from datetime import datetime
from typing import Any

from src.const import RECORDING_FOLDER


class Recorder:
    """Record and replay protobuf messages and GameState snapshots.

    Usage:
        rec = Recorder(directory="./recordings", max_in_memory=1000)
        rec.start_session("session-1")
        rec.record_message(bot_id, msg_bytes, msg_full_name, from_server=True)
        rec.snapshot_state(bot_id, state_dict)
        rec.stop_session()
        rec.replay(bot, path, preserve_timing=False)
    """

    def __init__(self, max_in_memory: int = 3_000):
        os.makedirs(RECORDING_FOLDER, exist_ok=True)
        self.max_record_in_memory = max_in_memory
        self._ring: list[dict[str, Any]] = []
        self._lock = threading.RLock()
        self._session_file: io.TextIOWrapper | None = None
        self._session_path: str | None = None

    def start_session(self, session_id: str | None = None) -> str:
        with self._lock:
            start_time = datetime.now().strftime("%Y%m%dT%H%M%SZ")
            session_id = session_id or f"rec_{start_time}"
            path = os.path.join(RECORDING_FOLDER, f"{session_id}.jsonl")
            self._session_file = open(path, "a", encoding="utf-8")
            self._session_path = path
            return path

    def stop_session(self) -> str | None:
        with self._lock:
            if self._session_file:
                try:
                    self._session_file.flush()
                    self._session_file.close()
                finally:
                    path = self._session_path
                    self._session_file = None
                    self._session_path = None
                    return path
            return None

    def save(self, path: str) -> None:
        """Flush current ring buffer to a file (append)."""
        with self._lock:
            with open(path, "a", encoding="utf-8") as file:
                for rec in self._ring:
                    file.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def record_message(
        self,
        bot_id: str,
        msg_bytes: bytes,
        msg_full_name: str,
        from_server: bool,
        timestamp: str | None = None,
    ) -> None:
        ts = timestamp or datetime.now().isoformat() + "Z"
        payload_b64 = base64.b64encode(msg_bytes).decode("ascii")
        rec = {
            "type": "message",
            "bot_id": bot_id,
            "from_server": bool(from_server),
            "msg_full_name": msg_full_name,
            "payload_b64": payload_b64,
            "timestamp": ts,
        }
        self._append_record(rec)

    def snapshot_state(
        self, bot_id: str, state_dict: dict[str, Any], timestamp: str | None = None
    ) -> None:
        ts = timestamp or datetime.now().isoformat() + "Z"
        rec = {
            "type": "state",
            "bot_id": bot_id,
            "state": state_dict,
            "timestamp": ts,
        }
        self._append_record(rec)

    def _append_record(self, rec: dict[str, Any]) -> None:
        line = json.dumps(rec, ensure_ascii=False)
        with self._lock:
            # write to session file if active
            if self._session_file:
                self._session_file.write(line + "\n")
                self._session_file.flush()
            # keep ring buffer limited
            self._ring.append(rec)
            if len(self._ring) > self.max_record_in_memory:
                self._ring.pop(0)

    def load(self, path: str) -> Iterator[dict[str, Any]]:
        """Yield records from a JSONL file in order."""
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)
