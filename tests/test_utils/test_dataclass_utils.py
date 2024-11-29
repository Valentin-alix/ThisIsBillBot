from dataclasses import dataclass, field
import unittest

from src.utils.dataclass_utils import reset_fields_to_default


@dataclass
class SampleState:
    value: int = 0
    labels: list[str] = field(default_factory=lambda: ["initial"])


class TestDataclassUtils(unittest.TestCase):
    def test_reset_fields_to_default(self) -> None:
        state = SampleState(value=42, labels=["changed"])

        reset_fields_to_default(state, ["value", "labels"])

        self.assertEqual(state.value, 0)
        self.assertEqual(state.labels, ["initial"])
