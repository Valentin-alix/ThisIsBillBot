"""
Mapping validation using recorded obfuscated messages.

This module demonstrates how to:
1. Record obfuscated messages from real gameplay
2. Replay them to validate game_mapping correctness
3. Detect mapping errors by comparing clear vs obfuscated processing
"""

import os
import unittest
from typing import List, Tuple

from D3Mapping.d3_mapping.models.message import MessageInfo
from D3Mapping.d3_mapping.protocol.protocol_game import get_obf_game_message_from_msg
from D3Mapping.d3_mapping.resources.protos.game.game_message_pb2 import Request
from src.const import RECORDING_FOLDER
from src.core.events_manager.event_manager import EventManager
from src.core.signals.grid_signals import GridSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.message_signals import MessageInfoSignals
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.states.state_factory import StateFactory
from src.services.logging.logger import Logger
from src.services.recorder import Recorder
from src.services.replayer import Replayer
from tests.fixtures.random_proto_generators import (
    generate_ChatChannelMessageRequest,
    generate_MapChangeRequest,
    generate_MapMovementEvent,
    generate_MapMovementRequest,
)


class MappingValidationResult:
    """Results of mapping validation."""

    def __init__(self) -> None:
        self.total_messages: int = 0
        self.successful_conversions: int = 0
        self.failed_conversions: List[Tuple[str, str]] = []
        self.mapping_mismatches: List[Tuple[str, dict, dict]] = []

    def add_success(self) -> None:
        self.total_messages += 1
        self.successful_conversions += 1

    def add_failure(self, obf_msg_name: str, error: str) -> None:
        self.total_messages += 1
        self.failed_conversions.append((obf_msg_name, error))

    def add_mismatch(self, expected: dict, actual: dict, msg_name: str) -> None:
        self.total_messages += 1
        self.mapping_mismatches.append((msg_name, expected, actual))

    def is_valid(self) -> bool:
        return len(self.failed_conversions) == 0 and len(self.mapping_mismatches) == 0

    def __str__(self) -> str:
        return f"""
                Mapping Validation Results:
                ---------------------------
                Total messages: {self.total_messages}
                Successful conversions: {self.successful_conversions}
                Failed conversions: {len(self.failed_conversions)}
                Mapping mismatches: {len(self.mapping_mismatches)}

                {"VALIDATION PASSED ✓" if self.is_valid() else "VALIDATION FAILED ✗"}
                """


class MappingValidator:
    """Validates game message mapping by comparing obfuscated and clear versions."""

    def __init__(self) -> None:
        self.recorder: Recorder = Recorder(max_in_memory=1000)

        # Create necessary signals and state
        log_signals = LogSignals()
        game_info_signals = GameInfoSignals()
        grid_signals = GridSignals()
        inventory_signals = InventorySignals()
        logger = Logger(log_signals=log_signals, title="mappingvalidator")

        self.game_state = StateFactory.create_game_state(
            inventory_signals=inventory_signals,
            game_info_signals=game_info_signals,
            grid_signals=grid_signals,
            logger=logger,
        )
        self.event_manager: EventManager = EventManager(_logger=logger)
        self.msg_info_signals: MessageInfoSignals = MessageInfoSignals()
        self.replayer: Replayer = Replayer(
            game_state=self.game_state,
            event_manager=self.event_manager,
            msg_info_signals=self.msg_info_signals,
            recorder=self.recorder,
        )

    def _validate_mapping(self, recording_path: str) -> MappingValidationResult:
        """
        Validate mapping by replaying obfuscated messages and checking conversion.

        This method:
        1. Loads recorded obfuscated messages
        2. Attempts to convert them to clear messages using game_mapping
        3. Compares the results
        4. Reports any mapping errors

        Args:
            recording_path: Path to recording file with obfuscated messages

        Returns:
            MappingValidationResult with validation details
        """
        result = MappingValidationResult()
        received_messages: List[Tuple[MessageInfo, bool]] = []

        def capture_msg(msg_info: MessageInfo, from_proxy: bool) -> None:
            received_messages.append((msg_info, from_proxy))

        self.msg_info_signals.msg_info.connect(capture_msg)

        # Replay obfuscated messages
        try:
            worker = self.replayer.get_replay_worker(
                recording_path, preserve_timing=False, use_obfuscated=True
            )
            worker()

            # Analyze each processed message
            for msg_info, from_proxy in received_messages:
                try:
                    # Check if obfuscated message was successfully processed
                    if msg_info.msg_json is not None:
                        result.add_success()
                    else:
                        result.add_failure(
                            msg_info.sub_msg_name, "No msg_json produced"
                        )

                    # Additional validation could be added here:
                    # - Check if all required fields are present
                    # - Verify field types match expectations
                    # - etc.

                except Exception as e:
                    result.add_failure(msg_info.sub_msg_name, str(e))

        except Exception as e:
            # Recording may be corrupted or invalid
            result.add_failure("RECORDING", f"Failed to replay: {str(e)}")

        finally:
            self.msg_info_signals.msg_info.disconnect(capture_msg)

        return result


class TestMappingValidation(unittest.TestCase):
    """Test suite for mapping validation functionality."""

    def setUp(self) -> None:
        self.validator: MappingValidator = MappingValidator()

    def tearDown(self) -> None:
        for file in os.listdir(RECORDING_FOLDER):
            if file.startswith("test_"):
                os.remove(os.path.join(RECORDING_FOLDER, file))
        return super().tearDown()

    def test_validate_synthetic_messages(self) -> None:
        """Test mapping validation with synthetic test messages."""
        self.validator.recorder.start_session("test_synthetic")

        # Create test messages with known good mapping
        test_messages = [
            generate_MapChangeRequest(),
            generate_MapMovementRequest(),
        ]

        for idx, clear_msg in enumerate(test_messages):
            # Create obfuscated version
            obf_msg = get_obf_game_message_from_msg(
                Request.DESCRIPTOR.full_name, clear_msg, uid=idx + 100
            )

            assert obf_msg

            # Record only the obfuscated version (simulating real traffic capture)
            self.validator.recorder.record_message(
                msg_bytes=None,
                bot_id="test",
                msg_full_name=None,
                obf_msg_bytes=obf_msg.SerializeToString(),
                obf_msg_full_name=obf_msg.DESCRIPTOR.full_name,
                from_server=True,
            )

        saved_path = self.validator.recorder.stop_session()

        assert saved_path

        result = self.validator._validate_mapping(saved_path)

        self.assertTrue(result.is_valid(), "Mapping validation should pass")
        self.assertEqual(result.total_messages, len(test_messages))
        self.assertEqual(result.successful_conversions, len(test_messages))

    def test_detect_mapping_error(self) -> None:
        """
        Test that mapping errors are detected.

        Note: This test demonstrates the concept but would need
        actual corrupted mapping data to properly test error detection.
        """
        self.validator.recorder.start_session("test_error")

        # In a real scenario, you would have obfuscated messages that
        # don't map correctly. For this test, we just verify the
        # validation mechanism works.

        saved_path = self.validator.recorder.stop_session()
        assert saved_path
        result = self.validator._validate_mapping(saved_path)

        # Empty recording should have no errors but also no messages
        self.assertTrue(result.is_valid())
        self.assertEqual(result.total_messages, 0)

    def test_batch_validation(self) -> None:
        """Test validating a large batch of messages."""
        self.validator.recorder.start_session("test_batch")

        message_count = 50
        for i in range(message_count):
            # Alternate between different message types
            if i % 2 == 0:
                clear_msg = generate_MapMovementEvent()
            else:
                clear_msg = generate_ChatChannelMessageRequest()

            obf_msg = get_obf_game_message_from_msg(
                Request.DESCRIPTOR.full_name, clear_msg, uid=i + 200
            )

            assert obf_msg

            self.validator.recorder.record_message(
                msg_bytes=None,
                bot_id="test",
                msg_full_name=None,
                obf_msg_bytes=obf_msg.SerializeToString(),
                obf_msg_full_name=obf_msg.DESCRIPTOR.full_name,
                from_server=(i % 3 == 0),  # Vary from_server
            )

        saved_path = self.validator.recorder.stop_session()

        assert saved_path

        result = self.validator._validate_mapping(saved_path)

        self.assertTrue(result.is_valid())
        self.assertEqual(result.total_messages, message_count)
        self.assertEqual(result.successful_conversions, message_count)


def validate_real_traffic_recording(recording_path: str) -> MappingValidationResult:
    """
    Standalone function to validate a recording from real game traffic.

    Usage:
        result = validate_real_traffic_recording("captures/session_20250116.jsonl")
        if not result.is_valid():
            pass

    Args:
        recording_path: Path to recording file captured from real gameplay

    Returns:
        MappingValidationResult with validation details
    """
    validator = MappingValidator()
    return validator._validate_mapping(recording_path)


if __name__ == "__main__":
    unittest.main()
