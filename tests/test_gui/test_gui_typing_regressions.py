import os
import unittest
from typing import cast

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from src.gui.components.multi_selection_combobox import MultiSelectComboBox
from src.gui.components.qfluent_widget.dynamic_tree_widget import DynamicTreeWidget
from src.gui.pages.debugs.message_table import MessageTable


def get_qapplication() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    return cast(QApplication, application)


class GuiTypingRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = get_qapplication()

    def test_multi_select_combo_box_updates_selection_and_display_text(self) -> None:
        combo_box = MultiSelectComboBox()
        combo_box.addItem("Alpha", userData="a")
        combo_box.addItem("Beta", userData="b")

        combo_box._onItemToggled(0, True)
        combo_box._onItemToggled(1, True)

        self.assertEqual(combo_box.selectedItemsData(), ["a", "b"])
        self.assertEqual(combo_box.text(), "Alpha, Beta")

    def test_multi_select_combo_box_clears_display_when_all_items_are_unselected(self) -> None:
        combo_box = MultiSelectComboBox()
        combo_box.addItem("Alpha", userData="a")

        combo_box._onItemToggled(0, True)
        combo_box._onItemToggled(0, False)

        self.assertEqual(combo_box.selectedItemsData(), [])
        self.assertEqual(combo_box.text(), "")

    def test_dynamic_tree_widget_builds_items_from_nested_content(self) -> None:
        tree_widget = DynamicTreeWidget()
        tree_widget.set_content(
            {
                "root": {
                    "child": "value",
                    "items": ["first", {"second": "value"}],
                }
            }
        )

        self.assertEqual(tree_widget.topLevelItemCount(), 1)
        root_item = tree_widget.topLevelItem(0)
        self.assertIsNotNone(root_item)
        assert root_item is not None
        self.assertEqual(root_item.text(0), "root")
        self.assertGreater(root_item.childCount(), 0)

    def test_message_table_deep_count_fields_counts_nested_dicts_and_lists(self) -> None:
        message_table = MessageTable()
        count = message_table.deep_count_fields(
            "ExampleMessage",
            {
                "first": {"nested": 1},
                "second": [1, {"leaf": 2}],
            },
        )

        self.assertEqual(count, 5)

    def test_message_table_deep_count_fields_returns_one_for_scalar_payload(self) -> None:
        message_table = MessageTable()

        self.assertEqual(message_table.deep_count_fields("ScalarMessage", "value"), 1)
