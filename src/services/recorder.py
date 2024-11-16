import base64
import io
import json
import os
import threading
from collections.abc import Iterator
from datetime import datetime
from typing import Any

from google.protobuf.descriptor import Descriptor
from google.protobuf.message_factory import GetMessageClass
from google.protobuf.proto import Message

from D3Mapping.d3_mapping.protocol.protocol_game import POOL
from src.const import RECORDING_FOLDER
from src.core.states.game_state import GameState
from src.utils.dataclass_utils import dataclass_to_dict


class Recorder:
    """Record and replay protobuf messages and GameState snapshots.

    Usage:
        rec = Recorder(directory="./recordings", max_in_memory=50_000)
        rec.start_session("session-1")
        rec.record_message(bot_id, msg_bytes, msg_full_name, from_server=True)
        rec.snapshot_state(bot_id, state_dict)
        rec.stop_session()
        rec.replay(bot, path, preserve_timing=False)
    """

    def __init__(self, max_in_memory: int = 50_000):
        os.makedirs(RECORDING_FOLDER, exist_ok=True)
        self.max_record_in_memory = max_in_memory
        self._ring: list[dict[str, Any]] = []
        self._lock = threading.RLock()
        self._session_file: io.TextIOWrapper | None = None
        self._session_path: str | None = None
        start_time = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        self.session_id: str = f"rec_{start_time}"

    def start_session(self, session_id: str | None = None) -> str:
        with self._lock:
            start_time = datetime.now().strftime("%Y%m%dT%H%M%SZ")
            self.session_id = session_id or f"rec_{start_time}"
            path = os.path.join(RECORDING_FOLDER, f"{self.session_id}.jsonl")
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

    def record_message_with_clear_and_obf_msg(
        self,
        bot_id: str,
        game_state: GameState,
        clear_sub_msg: Message | None,
        obf_sub_msg: Message,
        from_server: bool,
    ):
        if clear_sub_msg:
            if any(
                msg_name in clear_sub_msg.DESCRIPTOR.full_name
                for msg_name in [
                    "MapComplementaryInformationEvent",
                    "IdentificationRequest",
                ]
            ):
                self.snapshot_state(
                    bot_id,
                    dataclass_to_dict(game_state),
                )
            payload = clear_sub_msg.SerializeToString()
            msg_full_name = clear_sub_msg.DESCRIPTOR.full_name
        else:
            payload = None
            msg_full_name = None

        obf_payload = None
        obf_full_name = None
        if obf_sub_msg is not None:
            obf_payload = obf_sub_msg.SerializeToString()
            obf_full_name = obf_sub_msg.DESCRIPTOR.full_name

        self.record_message(
            bot_id,
            payload,
            msg_full_name,
            from_server,
            obf_msg_bytes=obf_payload,
            obf_msg_full_name=obf_full_name,
        )

    def record_message(
        self,
        bot_id: str,
        msg_bytes: bytes | None,
        msg_full_name: str | None,
        from_server: bool,
        timestamp: str | None = None,
        obf_msg_bytes: bytes | None = None,
        obf_msg_full_name: str | None = None,
    ) -> None:
        """
        Record a message (clear, obfuscated, or both).

        Args:
            bot_id: Bot identifier
            msg_bytes: Clear message bytes (can be None if only obfuscated)
            msg_full_name: Clear message full name (can be None if only obfuscated)
            from_server: Whether message is from server
            timestamp: Optional timestamp
            obf_msg_bytes: Obfuscated message bytes (optional)
            obf_msg_full_name: Obfuscated message full name (optional)

        Note:
            At least one of (msg_bytes, msg_full_name) or (obf_msg_bytes, obf_msg_full_name)
            must be provided.
        """
        if (msg_bytes is None or msg_full_name is None) and (
            obf_msg_bytes is None or obf_msg_full_name is None
        ):
            raise ValueError(
                "At least one message (clear or obfuscated) must be provided"
            )

        ts = timestamp or datetime.now().isoformat() + "Z"
        rec = {
            "type": "message",
            "bot_id": bot_id,
            "from_server": bool(from_server),
            "timestamp": ts,
        }

        # Add clear message if provided
        if msg_bytes is not None and msg_full_name is not None:
            payload_b64 = base64.b64encode(msg_bytes).decode("ascii")
            rec["msg_full_name"] = msg_full_name
            rec["payload_b64"] = payload_b64

        # Add obfuscated message if provided
        if obf_msg_bytes is not None and obf_msg_full_name is not None:
            obf_payload_b64 = base64.b64encode(obf_msg_bytes).decode("ascii")
            rec["obf_msg_full_name"] = obf_msg_full_name
            rec["obf_payload_b64"] = obf_payload_b64

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

    def deserialize_record(self, record: dict[str, Any]) -> Message | None:
        """Deserialize a message record back to a protobuf Message."""
        if "msg_full_name" not in record or "payload_b64" not in record:
            return None
        full_name = record["msg_full_name"]
        payload = base64.b64decode(record["payload_b64"])
        msg_descriptor: Descriptor = POOL.FindMessageTypeByName(full_name)
        msg_type = GetMessageClass(msg_descriptor)
        msg = msg_type()
        msg.ParseFromString(payload)
        return msg
