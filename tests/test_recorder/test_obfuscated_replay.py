"""
Tests for obfuscated message recording and replay.

This module tests:
1. Recording and replaying obfuscated messages
2. Recording only obfuscated messages (without clear version)
3. Converting obfuscated to clear during replay for mapping validation
4. Emitting messages correctly during replay
"""

import os
import time
import unittest
from datetime import datetime
from typing import List, Tuple

from D3Mapping.d3_mapping.models.message import MessageInfo
from D3Mapping.d3_mapping.protocol.protocol_game import get_obf_game_message_from_msg
from D3Mapping.d3_mapping.resources.protos.game.game_message_pb2 import Request
from src.const import RECORDING_FOLDER
from src.core.events_manager.event_manager import EventManager
from src.core.signals.message_signals import MessageInfoSignals
from src.services.recorder import Recorder
from src.services.replayer import Replayer
from tests.fixtures.random_proto_generators import generate_ChatChannelMessageRequest, generate_MapMovementRequest
from tests.setup_factory import GameStateFixture


class TestObfuscatedReplay(GameStateFixture):
    """Test suite for obfuscated message recording and replay."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        super().setUp()
        self.recorder: Recorder = Recorder(max_in_memory=100)
        self.msg_info_signals: MessageInfoSignals = MessageInfoSignals()
        self.event_manager_replay: EventManager = EventManager(_logger=self.logger)
        self.replayer: Replayer = Replayer(
            game_state=self.game_state,
            event_manager=self.event_manager_replay,
            msg_info_signals=self.msg_info_signals,
            recorder=self.recorder,
        )
        self.received_messages: List[Tuple[MessageInfo, bool]] = []
        self.msg_info_signals.msg_info.connect(self._on_msg_received)

    def tearDown(self) -> None:
        for file in os.listdir(RECORDING_FOLDER):
            if file.startswith("test_"):
                os.remove(os.path.join(RECORDING_FOLDER, file))
        return super().tearDown()

    def _on_msg_received(self, msg_info: MessageInfo, from_proxy: bool) -> None:
        """Callback to capture emitted messages."""
        self.received_messages.append((msg_info, from_proxy))

    def test_record_and_replay_both_clear_and_obfuscated(self) -> None:
        """Test recording both clear and obfuscated messages, then replaying clear."""
        self.recorder.start_session("test_both")

        clear_sub_msg = generate_MapMovementRequest()
        clear_payload = clear_sub_msg.SerializeToString()
        clear_full_name = clear_sub_msg.DESCRIPTOR.full_name

        obf_msg = get_obf_game_message_from_msg(Request.DESCRIPTOR.full_name, clear_sub_msg, uid=1)
        assert obf_msg
        obf_payload = obf_msg.SerializeToString()
        obf_full_name = obf_msg.DESCRIPTOR.full_name

        self.recorder.record_message(
            bot_id="test_bot",
            msg_bytes=clear_payload,
            msg_full_name=clear_full_name,
            from_server=True,
            obf_msg_bytes=obf_payload,
            obf_msg_full_name=obf_full_name,
        )

        saved_path = self.recorder.stop_session()
        assert saved_path
        self.assertIsNotNone(saved_path)
        self.assertTrue(os.path.exists(saved_path))

        # Replay clear version
        worker = self.replayer.get_replay_worker(saved_path, preserve_timing=False, use_obfuscated=False)
        worker()

        # Verify message was emitted
        self.assertEqual(len(self.received_messages), 1)
        msg_info, from_proxy = self.received_messages[0]
        self.assertEqual(msg_info.sub_msg_name, clear_sub_msg.__class__.__name__)
        self.assertTrue(msg_info.from_server)
        # Verify obf_msg_json is present
        self.assertIsNotNone(msg_info.obf_msg_json)

    def test_record_and_replay_obfuscated_only(self) -> None:
        """Test recording only obfuscated messages (no clear version)."""
        self.recorder.start_session("test_obf_only")

        # Generate a clear message then obfuscate it
        clear_msg = generate_ChatChannelMessageRequest()
        obf_msg = get_obf_game_message_from_msg(Request.DESCRIPTOR.full_name, clear_msg, uid=2)
        assert obf_msg
        obf_payload = obf_msg.SerializeToString()
        obf_full_name = obf_msg.DESCRIPTOR.full_name

        # Record ONLY obfuscated (no clear)
        self.recorder.record_message(
            bot_id="test_bot",
            msg_bytes=None,  # No clear version
            msg_full_name=None,
            from_server=False,
            obf_msg_bytes=obf_payload,
            obf_msg_full_name=obf_full_name,
        )

        saved_path = self.recorder.stop_session()
        assert saved_path

        # Replay - should automatically use obfuscated since clear is not available
        worker = self.replayer.get_replay_worker(saved_path, preserve_timing=False, use_obfuscated=False)
        worker()

        # Verify obfuscated message was replayed
        self.assertEqual(len(self.received_messages), 1)
        msg_info, from_proxy = self.received_messages[0]
        # The message class name should be the obfuscated one
        assert msg_info.sub_msg_name == obf_full_name
        self.assertFalse(msg_info.from_server)

    def test_validate_mapping_via_replay(self) -> None:
        """
        Test that we can validate game mapping by replaying obfuscated messages.

        This simulates the use case where we:
        1. Record obfuscated messages from real game
        2. Replay them through the mapping system
        3. Check if they process correctly
        """
        self.recorder.start_session("test_mapping_validation")

        # Create multiple obfuscated messages
        messages = [
            generate_MapMovementRequest(),
            generate_ChatChannelMessageRequest(),
        ]

        for idx, clear_msg in enumerate(messages):
            obf_msg = get_obf_game_message_from_msg(Request.DESCRIPTOR.full_name, clear_msg, uid=idx + 10)
            assert obf_msg
            obf_payload = obf_msg.SerializeToString()
            obf_full_name = obf_msg.DESCRIPTOR.full_name

            # Record both for comparison
            self.recorder.record_message(
                bot_id="test_bot",
                msg_bytes=clear_msg.SerializeToString(),
                msg_full_name=clear_msg.DESCRIPTOR.full_name,
                from_server=True,
                obf_msg_bytes=obf_payload,
                obf_msg_full_name=obf_full_name,
            )

        saved_path = self.recorder.stop_session()

        assert saved_path

        # Replay and verify all messages are processed
        worker = self.replayer.get_replay_worker(saved_path, preserve_timing=False, use_obfuscated=False)
        worker()

        # All messages should have been emitted
        self.assertEqual(len(self.received_messages), len(messages))

        # Each message should have obf_msg_json for validation
        for msg_info, from_proxy in self.received_messages:
            self.assertIsNotNone(
                msg_info.obf_msg_json,
                f"Message {msg_info.sub_msg_name} missing obf_msg_json",
            )
            self.assertTrue(msg_info.from_server)

    def test_error_when_no_message_provided(self) -> None:
        """Test that recording fails when neither clear nor obfuscated is provided."""
        self.recorder.start_session("test_error")

        with self.assertRaises(ValueError) as context:
            self.recorder.record_message(
                bot_id="test_bot",
                msg_bytes=None,
                msg_full_name=None,
                from_server=True,
                obf_msg_bytes=None,
                obf_msg_full_name=None,
            )

        self.assertIn("At least one message", str(context.exception))
        self.recorder.stop_session()

    def test_replay_empty_recording(self) -> None:
        """Test replaying a recording with no messages."""
        self.recorder.start_session("test_empty")
        saved_path = self.recorder.stop_session()

        assert saved_path

        worker = self.replayer.get_replay_worker(saved_path, preserve_timing=False, use_obfuscated=False)
        worker()

        # No messages should be received
        self.assertEqual(len(self.received_messages), 0)

    def test_message_timing_preserved(self) -> None:
        """Test that message timing can be preserved during replay."""
        self.recorder.start_session("test_timing")

        # Record messages with specific timestamps
        base_time = datetime.now()
        timestamps = [
            base_time.isoformat() + "Z",
            (base_time.replace(microsecond=base_time.microsecond + 100000)).isoformat() + "Z",
        ]

        for ts in timestamps:
            clear_msg = generate_MapMovementRequest()
            self.recorder.record_message(
                bot_id="test_bot",
                msg_bytes=clear_msg.SerializeToString(),
                msg_full_name=clear_msg.DESCRIPTOR.full_name,
                from_server=True,
                timestamp=ts,
            )

        saved_path = self.recorder.stop_session()

        assert saved_path

        # Replay with timing preservation
        start_replay = time.time()
        worker = self.replayer.get_replay_worker(
            saved_path,
            preserve_timing=True,
            speedup=10.0,  # 10x faster
        )
        worker()
        end_replay = time.time()

        # Verify messages were received
        self.assertEqual(len(self.received_messages), 2)

        # Timing should be much faster due to speedup
        replay_duration = end_replay - start_replay
        self.assertLess(replay_duration, 1.0)  # Should be very fast with 10x speedup


if __name__ == "__main__":
    unittest.main()
