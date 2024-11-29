import unittest

from src.utils.json_utils import JSONValue, flatten_json


class TestJsonUtils(unittest.TestCase):
    def test_flatten_json_nested_structure(self) -> None:
        payload: JSONValue = {"a": 1, "b": [2, {"c": "x"}]}

        self.assertEqual(flatten_json(payload), " a = 1 b.0 = 2 b.1.c = x")
