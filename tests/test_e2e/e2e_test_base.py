from datetime import datetime
from pathlib import Path

from src.services.recorder import Recorder
from tests.test_behaviors.behavior_test_base import BehaviorTestBase
from tests.test_e2e.validators.base import (
    RecordedMessage,
    SequenceValidator,
    ValidationResult,
)

RECORDINGS_DIR = Path(__file__).parent / "recordings"


class E2ETestBase(BehaviorTestBase):

    def setUp(self):
        super().setUp()
        self.recorder = Recorder()
        self.validators: list[SequenceValidator] = []

    def load_recording(self, name: str) -> str:
        path = RECORDINGS_DIR / f"{name}.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"Recording not found: {path}")
        return str(path)

    def extract_all_messages(self, path: str) -> list[RecordedMessage]:
        messages: list[RecordedMessage] = []
        for record in self.recorder.load(path):
            if record.get("type") != "message":
                continue
            msg = self.recorder.deserialize_record(record)
            if msg is None:
                continue
            timestamp = self._parse_timestamp(record["timestamp"])
            messages.append(
                RecordedMessage(
                    msg=msg,
                    timestamp=timestamp,
                    from_server=record.get("from_server", False),
                    msg_type_name=type(msg).__name__,
                )
            )
        return messages

    def _parse_timestamp(self, ts_str: str) -> float:
        ts_clean = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_clean)
        return dt.timestamp()

    def register_validator(self, validator: SequenceValidator):
        self.validators.append(validator)

    def validate_recording(self, path: str) -> list[ValidationResult]:
        messages = self.extract_all_messages(path)
        all_results: list[ValidationResult] = []

        for validator in self.validators:
            if validator.applies_to(messages):
                results = validator.validate(messages)
                all_results.extend(results)

        return all_results

    def assert_recording_valid(self, path: str):
        results = self.validate_recording(path)
        failures = [r for r in results if not r.is_valid]

        if failures:
            failure_msgs = [f"- {r.reason}: {r.details}" for r in failures]
            raise AssertionError(
                f"Validation failed with {len(failures)} error(s):\n"
                + "\n".join(failure_msgs)
            )
