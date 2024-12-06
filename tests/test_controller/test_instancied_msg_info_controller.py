import os
import unittest

from google.protobuf.field_mask_pb2 import FieldMask
from pandas import DataFrame

from src.controller.instancied_msg_info_controller import (
    InstanciedMessageInfoController,
)


class InstanciedMessageInfoControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ.setdefault("PC_ID", "test")
        self.controller = InstanciedMessageInfoController()
        self.controller._df = DataFrame(columns=["name", "content"])
        self.controller._rows_to_add_by_name.clear()
        self.controller._total_pending_rows = 0
        if hasattr(self.controller, "get_count_by_name_in_df"):
            del self.controller.get_count_by_name_in_df

    def tearDown(self) -> None:
        self.controller._rows_to_add_by_name.clear()
        self.controller._total_pending_rows = 0

    def test_update_msg_infos_content_serializes_repeated_scalar_fields(self) -> None:
        message = FieldMask(paths=["alpha", "beta"])

        serialized = self.controller._update_msg_infos_content(message, from_server=False)

        self.assertEqual(serialized["paths"], ["alpha", "beta"])
        self.assertEqual(self.controller._total_pending_rows, 1)
        self.assertEqual(
            self.controller._rows_to_add_by_name[message.DESCRIPTOR.full_name][0]["content"],
            serialized,
        )

    def test_update_msg_infos_content_keeps_empty_repeated_scalar_fields(self) -> None:
        message = FieldMask()

        serialized = self.controller._update_msg_infos_content(message, from_server=False)

        self.assertEqual(serialized["paths"], [])
