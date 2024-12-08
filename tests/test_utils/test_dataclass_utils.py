from dataclasses import dataclass, field
import unittest

from src.utils.dataclass_utils import (
    is_serialized_content,
    is_serialized_value,
    reset_fields_to_default,
)


@dataclass
class SampleState:
    value: int = 0
    labels: list[str] = field(default_factory=lambda: ["initial"])


@dataclass
class InitFalseState:
    labels: list[int] = field(init=False, default_factory=list[int])


class TestDataclassUtils(unittest.TestCase):
    def test_reset_fields_to_default(self) -> None:
        state = SampleState(value=42, labels=["changed"])

        reset_fields_to_default(state, ["value", "labels"])

        self.assertEqual(state.value, 0)
        self.assertEqual(state.labels, ["initial"])

    def test_reset_fields_to_default_uses_default_factory_for_init_false_field(
        self,
    ) -> None:
        state = InitFalseState()
        state.labels.extend([1, 2, 3])

        reset_fields_to_default(state, ["labels"])

        self.assertEqual(state.labels, [])

    def test_is_serialized_value_accepts_nested_serialized_payloads(self) -> None:
        self.assertTrue(
            is_serialized_value(
                {
                    "msg_full_name": "google.protobuf.FieldMask",
                    "content": '{"paths":["alpha"]}',
                    "nested": [{"ok": True}],
                }
            )
        )

    def test_is_serialized_value_rejects_non_string_mapping_keys(self) -> None:
        self.assertFalse(is_serialized_value({1: "invalid"}))

    def test_is_serialized_content_rejects_invalid_nested_values(self) -> None:
        self.assertFalse(is_serialized_content({"alpha": object()}))
