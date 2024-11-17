import base64
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from D3Mapping.d3_mapping.models.message import MessageInfo
from D3Mapping.d3_mapping.protocol.protocol import parse_message_from_payload
from D3Mapping.d3_mapping.protocol.protocol_game import get_clear_msg_from_obf
from src.core.events_manager.event_manager import EventManager
from src.core.signals.message_signals import MessageInfoSignals
from src.core.states.game_state import GameState
from src.services.recorder import Recorder
from src.utils.protobuf_utils import apply_dict_to_dataclass


def _get_clear_message_from_obf(obf_msg: Message) -> tuple[dict, Message]:
    clear_msg = get_clear_msg_from_obf(obf_msg)
    if clear_msg is not None:
        return MessageToDict(clear_msg), clear_msg
    return MessageToDict(obf_msg), obf_msg


def _get_clear_message_from_record(
    record_line: dict,
) -> tuple[dict, Message]:
    clear_payload = base64.b64decode(record_line["payload_b64"])
    clear_full_name = record_line["msg_full_name"]
    clear_msg = parse_message_from_payload(clear_payload, clear_full_name)
    return MessageToDict(clear_msg), clear_msg


def _get_obf_message_from_record(record_line: dict) -> dict | None:
    if "obf_payload_b64" not in record_line:
        return None
    obf_payload = base64.b64decode(record_line["obf_payload_b64"])
    obf_full_name = record_line["obf_msg_full_name"]
    obf_msg = parse_message_from_payload(obf_payload, obf_full_name)
    return MessageToDict(obf_msg)


@dataclass
class Replayer:
    game_state: GameState
    event_manager: EventManager
    msg_info_signals: MessageInfoSignals
    recorder: Recorder

    def _prepare_clear_message_info(
        self, record_line: dict, msg: Message, use_obfuscated: bool
    ) -> tuple[dict, Message]:
        if use_obfuscated and "obf_payload_b64" in record_line:
            return _get_clear_message_from_obf(msg)

        if "payload_b64" in record_line:
            return _get_clear_message_from_record(record_line)

        return MessageToDict(msg), msg

    def get_replay_worker(
        self,
        path: str,
        preserve_timing: bool = False,
        speedup: float | None = None,
        use_obfuscated: bool = False,
        do_wait_state: bool = False,
    ) -> Callable:
        def _worker():
            did_apply_state: bool = False
            last_timestamp: float | None = None

            for record_line in self.recorder.load(path):
                if record_line.get("type") == "state":
                    apply_dict_to_dataclass(self.game_state, record_line["state"])
                    did_apply_state = True
                    continue

                if record_line.get("type") != "message":
                    continue

                if not did_apply_state and do_wait_state:
                    continue

                curr_timestamp = time.mktime(
                    datetime.fromisoformat(
                        record_line["timestamp"].replace("Z", "")
                    ).timetuple()
                )

                if preserve_timing:
                    self._handle_timing(curr_timestamp, last_timestamp, speedup)

                last_timestamp = curr_timestamp
                self._process_record_line(record_line, use_obfuscated)

        return _worker

    def _handle_timing(
        self, curr_timestamp: float, last_timestamp: float | None, speedup: float | None
    ) -> None:
        if last_timestamp is None:
            return
        wait = curr_timestamp - last_timestamp
        if speedup:
            wait = wait / speedup
        if wait > 0:
            time.sleep(wait)

    def _process_record_line(self, record_line: dict, use_obfuscated: bool) -> None:
        message_data = self._get_message_to_process(record_line, use_obfuscated)
        if message_data is None:
            return

        payload, full_name = message_data
        msg = parse_message_from_payload(payload, full_name)

        clear_msg_json, clear_msg = self._prepare_clear_message_info(
            record_line, msg, use_obfuscated
        )
        obf_msg_json = _get_obf_message_from_record(record_line)

        curr_timestamp = time.mktime(
            datetime.fromisoformat(
                record_line["timestamp"].replace("Z", "")
            ).timetuple()
        )

        msg_info = MessageInfo(
            received_time=datetime.fromtimestamp(curr_timestamp),
            from_server=record_line["from_server"],
            msg_json=clear_msg_json,
            sub_msg_name=clear_msg.__class__.__name__,
            obf_msg_json=obf_msg_json,
        )
        self.msg_info_signals.msg_info.emit(msg_info, False)
        self.event_manager.process_msg(clear_msg)

    def _get_message_to_process(
        self, record_line: dict, use_obfuscated: bool
    ) -> tuple[bytes, str] | None:
        if use_obfuscated and "obf_payload_b64" in record_line:
            payload = base64.b64decode(record_line["obf_payload_b64"])
            full_name = record_line["obf_msg_full_name"]
            return payload, full_name

        if not use_obfuscated and "payload_b64" in record_line:
            payload = base64.b64decode(record_line["payload_b64"])
            full_name = record_line["msg_full_name"]
            return payload, full_name

        if "obf_payload_b64" in record_line:
            payload = base64.b64decode(record_line["obf_payload_b64"])
            full_name = record_line["obf_msg_full_name"]
            return payload, full_name

        return None
