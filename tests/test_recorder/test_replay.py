import base64
import os
import time
import unittest
from unittest.mock import MagicMock

from D3Mapping.d3_mapping.models.message import MessageInfo
from src.const import RECORDING_FOLDER
from src.services.recorder import Recorder
from src.services.replayer import (
    Replayer,
    _get_clear_message_from_record,
    _get_obf_message_from_record,
)
from tests.fixtures.dummy_models import DummyBot
from tests.fixtures.random_generator import generate_random_bot
from tests.fixtures.random_proto_generators import generate_ExchangeCraftCountRequest


class TestReplayerHelpers(unittest.TestCase):
    def test_get_clear_message_from_record(self):
        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        payload_b64 = base64.b64encode(payload).decode()

        record_line = {
            "payload_b64": payload_b64,
            "msg_full_name": msg.DESCRIPTOR.full_name,
        }

        msg_json, clear_msg = _get_clear_message_from_record(record_line)

        assert isinstance(msg_json, dict)
        assert clear_msg.__class__.__name__ == "ExchangeCraftCountRequest"

    def test_get_obf_message_from_record_with_obf(self):
        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        payload_b64 = base64.b64encode(payload).decode()

        record_line = {
            "obf_payload_b64": payload_b64,
            "obf_msg_full_name": msg.DESCRIPTOR.full_name,
        }

        msg_json = _get_obf_message_from_record(record_line)

        assert isinstance(msg_json, dict)

    def test_get_obf_message_from_record_without_obf(self):
        record_line = {}
        msg_json = _get_obf_message_from_record(record_line)
        assert msg_json is None


class TestReplayerMethods(unittest.TestCase):
    def setUp(self):
        self.mock_game_state = MagicMock()
        self.mock_event_manager = MagicMock()
        self.mock_msg_info_signals = MagicMock()
        self.mock_recorder = MagicMock()

        self.replayer = Replayer(
            game_state=self.mock_game_state,
            event_manager=self.mock_event_manager,
            msg_info_signals=self.mock_msg_info_signals,
            recorder=self.mock_recorder,
        )

    def test_get_message_to_process_use_obfuscated_true(self):
        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        payload_b64 = base64.b64encode(payload).decode()

        record_line = {
            "obf_payload_b64": payload_b64,
            "obf_msg_full_name": msg.DESCRIPTOR.full_name,
            "payload_b64": payload_b64,
            "msg_full_name": msg.DESCRIPTOR.full_name,
        }

        result = self.replayer._get_message_to_process(record_line, use_obfuscated=True)

        assert result is not None
        payload_result, full_name = result
        assert payload_result == payload
        assert full_name == msg.DESCRIPTOR.full_name

    def test_get_message_to_process_use_obfuscated_false(self):
        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        payload_b64 = base64.b64encode(payload).decode()

        record_line = {
            "payload_b64": payload_b64,
            "msg_full_name": msg.DESCRIPTOR.full_name,
        }

        result = self.replayer._get_message_to_process(
            record_line, use_obfuscated=False
        )

        assert result is not None
        payload_result, full_name = result
        assert payload_result == payload
        assert full_name == msg.DESCRIPTOR.full_name

    def test_get_message_to_process_fallback_to_obf(self):
        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        payload_b64 = base64.b64encode(payload).decode()

        record_line = {
            "obf_payload_b64": payload_b64,
            "obf_msg_full_name": msg.DESCRIPTOR.full_name,
        }

        result = self.replayer._get_message_to_process(
            record_line, use_obfuscated=False
        )

        assert result is not None
        payload_result, full_name = result
        assert payload_result == payload
        assert full_name == msg.DESCRIPTOR.full_name

    def test_get_message_to_process_no_message(self):
        record_line = {}
        result = self.replayer._get_message_to_process(
            record_line, use_obfuscated=False
        )
        assert result is None

    def test_prepare_clear_message_info_from_record(self):
        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        payload_b64 = base64.b64encode(payload).decode()

        record_line = {
            "payload_b64": payload_b64,
            "msg_full_name": msg.DESCRIPTOR.full_name,
        }

        msg_json, clear_msg = self.replayer._prepare_clear_message_info(
            record_line, msg, use_obfuscated=False
        )

        assert isinstance(msg_json, dict)
        assert clear_msg.__class__.__name__ == "ExchangeCraftCountRequest"

    def test_prepare_clear_message_info_fallback_to_msg(self):
        msg = generate_ExchangeCraftCountRequest()
        record_line = {}

        msg_json, clear_msg = self.replayer._prepare_clear_message_info(
            record_line, msg, use_obfuscated=False
        )

        assert isinstance(msg_json, dict)
        assert clear_msg.__class__.__name__ == msg.__class__.__name__

    def test_handle_timing_with_speedup(self):
        start_time = time.time()
        self.replayer._handle_timing(1.0, 0.0, speedup=10.0)
        elapsed = time.time() - start_time
        assert elapsed < 0.2

    def test_handle_timing_without_speedup(self):
        start_time = time.time()
        self.replayer._handle_timing(0.1, 0.0, speedup=None)
        elapsed = time.time() - start_time
        assert elapsed >= 0.1 and elapsed < 0.2

    def test_process_record_line_no_message(self):
        record_line = {"timestamp": "2024-01-01T00:00:00"}
        self.replayer._process_record_line(record_line, use_obfuscated=False)
        self.mock_event_manager.process_msg.assert_not_called()

    def test_process_record_line_with_message(self):
        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        payload_b64 = base64.b64encode(payload).decode()

        record_line = {
            "payload_b64": payload_b64,
            "msg_full_name": msg.DESCRIPTOR.full_name,
            "timestamp": "2024-01-01T00:00:00",
            "from_server": True,
        }

        self.replayer._process_record_line(record_line, use_obfuscated=False)

        self.mock_event_manager.process_msg.assert_called_once()
        self.mock_msg_info_signals.msg_info.emit.assert_called_once()

        call_args = self.mock_msg_info_signals.msg_info.emit.call_args
        msg_info = call_args[0][0]
        assert isinstance(msg_info, MessageInfo)
        assert msg_info.from_server is True
        assert msg_info.msg_json is not None
        assert msg_info.sub_msg_name == "ExchangeCraftCountRequest"


class TestReplayerIntegration(unittest.TestCase):
    def test_record_and_replay_message_and_state(self):
        rec = Recorder(max_in_memory=100)
        path = rec.start_session("testsession")

        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        rec.record_message("bot1", payload, msg.DESCRIPTOR.full_name, from_server=True)
        rec.snapshot_state("bot1", {"player": {"foo": 42, "bar": "hello"}})

        saved = rec.stop_session()
        assert saved is not None and os.path.exists(saved)

        bot = DummyBot()
        mock_msg_info_signals = MagicMock()

        replayer = Replayer(
            game_state=bot.game_state,  # type: ignore
            event_manager=bot.event_manager,  # type: ignore
            msg_info_signals=mock_msg_info_signals,
            recorder=rec,
        )

        worker = replayer.get_replay_worker(
            path=saved, preserve_timing=False, use_obfuscated=False, do_wait_state=True
        )
        worker()

        assert bot.game_state.player.foo == 42
        assert len(bot.event_manager.received) >= 1

    def test_replay_snapshot(self):
        recording_path = os.path.join(RECORDING_FOLDER, "collect_&_fight.jsonl")
        if not os.path.exists(recording_path):
            self.skipTest(f"Recording file not found: {recording_path}")

        bot = generate_random_bot()
        bot.replay_handler.on_replay_requested(recording_path)

        print(bot.game_state.fight.count_casted_by_spell_id_on_current_turn)

        for thread, worker in bot._thread_worker_runnings:
            thread.wait()
