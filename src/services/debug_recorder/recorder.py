"""
Per-bot debug recorder. Captures logs + sniffer messages into a JSONL file in
chronological order (one DebugLogEntry / DebugMessageEntry per line).

Design:
- One background daemon thread per bot drains a queue, serializes entries and
  writes them to disk in batches.
- Hot paths (proxy worker threads, log emit) only push raw data into the queue
  (cheap, no Qt signals involved), so the GUI thread is not starved.
- The file is truncated at session start to bound size; rotation per-session.
"""

import atexit
import json
import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, TypedDict

from google.protobuf.message import Message

from src.protocol.protocol_connection import get_conn_msg_info
from src.protocol.protocol_game import get_game_msg_info


class DebugLogEntry(TypedDict):
    categorie: Literal["log"]
    datetime: str
    niveau: str
    message: str


class DebugMessageEntry(TypedDict):
    categorie: Literal["message"]
    datetime: str
    origine: str
    type_non_obfusque: str
    type_obfusque: str | None
    contenu_obfusque: dict[str, Any] | None
    contenu_non_obfusque: dict[str, Any] | None


DebugEntry = DebugLogEntry | DebugMessageEntry


def _parse_sub_msg_name(sub_msg_name: str) -> tuple[str | None, str]:
    if " -> " in sub_msg_name:
        obf, decoded = sub_msg_name.split(" -> ", 1)
        return obf, decoded
    return None, sub_msg_name


@dataclass(slots=True)
class _LogRaw:
    logged_at: datetime
    level: str
    message: str


@dataclass(slots=True)
class _GameMsgRaw:
    received_at: datetime
    clear_sub_msg: Message | None
    obf_sub_msg: Message
    uid: int | None
    from_server: bool


@dataclass(slots=True)
class _ConnMsgRaw:
    received_at: datetime
    sub_msg: Message
    from_server: bool


_RawEntry = _LogRaw | _GameMsgRaw | _ConnMsgRaw


_MAX_BUFFER = 100
_FLUSH_INTERVAL_S = 1.0


@dataclass
class DebugRecorder:
    file_path: str
    _queue: queue.Queue[_RawEntry | None] = field(
        init=False, default_factory=queue.Queue[_RawEntry | None]
    )
    _stop_event: threading.Event = field(init=False, default_factory=threading.Event)

    def __post_init__(self) -> None:
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        self._thread = threading.Thread(
            target=self._drain,
            daemon=True,
            name=f"DebugRecorder-{Path(self.file_path).stem}",
        )
        self._thread.start()
        atexit.register(self.stop)

    def record_log(self, level: str, message: str, logged_at: datetime) -> None:
        self._queue.put(_LogRaw(logged_at, level, message))

    def record_game_message(
        self,
        clear_sub_msg: Message | None,
        obf_sub_msg: Message,
        uid: int | None,
        from_server: bool,
    ) -> None:
        self._queue.put(
            _GameMsgRaw(datetime.now(), clear_sub_msg, obf_sub_msg, uid, from_server)
        )

    def record_conn_message(self, sub_msg: Message, from_server: bool) -> None:
        self._queue.put(_ConnMsgRaw(datetime.now(), sub_msg, from_server))

    def stop(self) -> None:
        if self._stop_event.is_set():
            return
        self._stop_event.set()
        self._queue.put(None)
        self._thread.join(timeout=5)

    def _drain(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as file:
            buffer: list[str] = []
            last_flush = time.monotonic()
            while True:
                try:
                    item = self._queue.get(timeout=_FLUSH_INTERVAL_S)
                except queue.Empty:
                    item = None
                    if self._stop_event.is_set():
                        self._flush(file, buffer)
                        return

                if item is not None:
                    entry = _build_entry(item)
                    buffer.append(json.dumps(entry, ensure_ascii=False))

                now = time.monotonic()
                if buffer and (
                    len(buffer) >= _MAX_BUFFER or now - last_flush >= _FLUSH_INTERVAL_S
                ):
                    self._flush(file, buffer)
                    last_flush = now

                if self._stop_event.is_set() and self._queue.empty():
                    self._flush(file, buffer)

    @staticmethod
    def _flush(file: Any, buffer: list[str]) -> None:
        if not buffer:
            return
        file.write("\n".join(buffer) + "\n")
        file.flush()
        buffer.clear()


def _build_entry(raw: _RawEntry) -> DebugEntry:
    if isinstance(raw, _LogRaw):
        return DebugLogEntry(
            categorie="log",
            datetime=raw.logged_at.isoformat(),
            niveau=raw.level,
            message=raw.message,
        )
    if isinstance(raw, _GameMsgRaw):
        msg_info = get_game_msg_info(
            raw.clear_sub_msg, raw.obf_sub_msg, raw.uid, raw.from_server, False
        )
        obf_type, decoded_type = _parse_sub_msg_name(msg_info.sub_msg_name)
        return DebugMessageEntry(
            categorie="message",
            datetime=msg_info.received_time.isoformat(),
            origine="Serveur" if msg_info.from_server else "Client",
            type_non_obfusque=decoded_type,
            type_obfusque=obf_type,
            contenu_obfusque=msg_info.obf_msg_json,
            contenu_non_obfusque=msg_info.msg_json,
        )
    # _ConnMsgRaw
    msg_info = get_conn_msg_info(raw.sub_msg, raw.from_server)
    obf_type, decoded_type = _parse_sub_msg_name(msg_info.sub_msg_name)
    return DebugMessageEntry(
        categorie="message",
        datetime=msg_info.received_time.isoformat(),
        origine="Serveur" if msg_info.from_server else "Client",
        type_non_obfusque=decoded_type,
        type_obfusque=obf_type,
        contenu_obfusque=msg_info.obf_msg_json,
        contenu_non_obfusque=msg_info.msg_json,
    )
