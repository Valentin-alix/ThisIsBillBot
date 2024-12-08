from dataclasses import dataclass, field
import unittest

from src.utils.protobuf_utils import apply_dict_to_dataclass


class CustomDict(dict[int, int]):
    pass


@dataclass
class NestedState:
    value: int = 0


@dataclass
class SampleState:
    nested: NestedState = field(default_factory=NestedState)
    values: CustomDict = field(default_factory=CustomDict)


class ProtobufUtilsTests(unittest.TestCase):
    def test_apply_dict_to_dataclass_preserves_custom_dict_type(self) -> None:
        state = SampleState(values=CustomDict({1: 2}))

        apply_dict_to_dataclass(state, {"values": {"3": "4"}})

        self.assertIsInstance(state.values, CustomDict)
        self.assertEqual(state.values, {1: 2, 3: 4})

    def test_apply_dict_to_dataclass_updates_nested_dataclass(self) -> None:
        state = SampleState()

        apply_dict_to_dataclass(state, {"nested": {"value": "7"}})

        self.assertEqual(state.nested.value, 7)

    def test_apply_dict_to_dataclass_rejects_invalid_serialized_proto_payload(self) -> None:
        state = SampleState()

        with self.assertRaises(TypeError):
            apply_dict_to_dataclass(
                state,
                {
                    "nested": {
                        "value": {
                            "msg_full_name": "google.protobuf.FieldMask",
                            "content": 1,
                        }
                    }
                },
            )
