import json
import unittest
from timeit import timeit

from google.protobuf.json_format import MessageToDict

from src.common.json_utils import flatten_json
from tests.fixtures.random_proto_generators import (
    generate_MapComplementaryInformationEvent,
)


class TestFlattenJons(unittest.TestCase):
    def test_flatten_json(self):
        msg_json = MessageToDict(generate_MapComplementaryInformationEvent())
        obf_msg_json = {"ied": "lalalaaa", "poo": {"lo": 1}}

        standard_dump = timeit(
            lambda: json.dumps(msg_json) + json.dumps(obf_msg_json), number=100_000
        )

        custom_dump = timeit(
            lambda: flatten_json(msg_json) + flatten_json(obf_msg_json), number=100_000
        )

        print(standard_dump, custom_dump)
