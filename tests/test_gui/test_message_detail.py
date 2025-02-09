import os
import unittest
from typing import cast

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from google.protobuf.descriptor import Descriptor
from PyQt6.QtWidgets import QApplication
from datas.protos.non_obf.game.inventory_pb2 import InventoryContentEvent

from src.gui.pages.debugs.message_detail import (
    ABSENT_FIELD_DISPLAY_VALUE,
    MessageDetailWidget,
    complete_message_tree_content,
    resolve_selected_pinned_field,
)


class TestCompleteMessageTreeContent(unittest.TestCase):
    def test_adds_absent_root_fields(self) -> None:
        completed = complete_message_tree_content(
            {"objects": []}, cast(Descriptor, InventoryContentEvent.DESCRIPTOR)
        )

        self.assertEqual(completed["objects"], [])
        self.assertEqual(completed["kamas"], ABSENT_FIELD_DISPLAY_VALUE)

    def test_completes_present_repeated_message_items(self) -> None:
        completed = complete_message_tree_content(
            {"objects": [{"position": 1}], "kamas": 10},
            cast(Descriptor, InventoryContentEvent.DESCRIPTOR),
        )

        first_object = completed["objects"][0]
        self.assertEqual(first_object["position"], 1)
        self.assertEqual(first_object["item"], ABSENT_FIELD_DISPLAY_VALUE)
        self.assertEqual(completed["kamas"], 10)


class TestMessageDetailWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_absent_root_fields_are_selectable_when_toggle_is_enabled(self) -> None:
        widget = MessageDetailWidget()
        widget.set_content(
            {"objects": []},
            {"a": 1},
            cast(Descriptor, InventoryContentEvent.DESCRIPTOR),
        )

        widget.show_absent_fields_btn.setChecked(True)
        widget._on_show_absent_fields_clicked()
        kamas_item = widget.dynamic_tree.topLevelItem(1)
        self.assertIsNotNone(kamas_item)

        widget.dynamic_tree.setCurrentItem(kamas_item)

        self.assertEqual(widget.dynamic_tree.selected_root_field_name(), "kamas")
        self.assertEqual(widget.dynamic_tree.selected_field_path(), ("kamas",))

    def test_nested_repeated_message_field_is_selectable(self) -> None:
        widget = MessageDetailWidget()
        content: dict[str, object] = {"objects": [{"position": 1}], "kamas": 10}
        descriptor = cast(Descriptor, InventoryContentEvent.DESCRIPTOR)
        widget.set_content(content, content, descriptor, descriptor)

        objects_item = widget.dynamic_tree.topLevelItem(0)
        assert objects_item is not None
        index_item = objects_item.child(0)
        assert index_item is not None
        position_item = index_item.child(0)
        assert position_item is not None

        widget.dynamic_tree.setCurrentItem(position_item)
        obf_objects_item = widget.obf_dynamic_tree.topLevelItem(0)
        assert obf_objects_item is not None
        obf_index_item = obf_objects_item.child(0)
        assert obf_index_item is not None
        obf_position_item = obf_index_item.child(0)
        assert obf_position_item is not None
        widget.obf_dynamic_tree.setCurrentItem(obf_position_item)

        fields = widget.selected_pinned_fields()
        assert fields is not None
        obf_field, non_obf_field = fields
        self.assertEqual(obf_field.field_name, "position")
        self.assertEqual(non_obf_field.field_name, "position")
        self.assertEqual(non_obf_field.path, ("objects", "position"))
        assert non_obf_field.container_descriptor is not None
        self.assertEqual(non_obf_field.container_descriptor.name, "ObjectItemInventory")

    def test_repeated_item_index_is_not_selectable_as_field(self) -> None:
        widget = MessageDetailWidget()
        content: dict[str, object] = {"objects": [{"position": 1}], "kamas": 10}
        descriptor = cast(Descriptor, InventoryContentEvent.DESCRIPTOR)
        widget.set_content(content, content, descriptor, descriptor)

        objects_item = widget.dynamic_tree.topLevelItem(0)
        assert objects_item is not None
        index_item = objects_item.child(0)
        assert index_item is not None

        widget.dynamic_tree.setCurrentItem(index_item)

        self.assertIsNone(widget.dynamic_tree.selected_field_path())

    def test_resolves_selected_pinned_field_from_descriptor_path(self) -> None:
        field = resolve_selected_pinned_field(
            cast(Descriptor, InventoryContentEvent.DESCRIPTOR),
            ("objects", "position"),
        )

        assert field is not None
        self.assertEqual(field.field_name, "position")
        assert field.container_descriptor is not None
        self.assertEqual(field.container_descriptor.name, "ObjectItemInventory")


if __name__ == "__main__":
    unittest.main()
