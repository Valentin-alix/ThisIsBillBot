from dataclasses import dataclass, field

from src.utils.dataclass_utils import (
    is_serialized_content,
    is_serialized_value,
)


@dataclass
class SampleState:
    value: int = 0
    labels: list[str] = field(default_factory=lambda: ["initial"])


@dataclass
class InitFalseState:
    labels: list[int] = field(init=False, default_factory=list[int])


class TestDataclassUtils:
    def test_is_serialized_value_accepts_nested_serialized_payloads(self) -> None:
        assert is_serialized_value(
            {
                "msg_full_name": "google.protobuf.FieldMask",
                "content": '{"paths":["alpha"]}',
                "nested": [{"ok": True}],
            }
        )

    def test_is_serialized_value_rejects_non_string_mapping_keys(self) -> None:
        assert not is_serialized_value({1: "invalid"})

    def test_is_serialized_content_rejects_invalid_nested_values(self) -> None:
        assert not is_serialized_content({"alpha": object()})
