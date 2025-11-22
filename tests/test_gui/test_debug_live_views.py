import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QEventLoop, Qt, QTimer
from PyQt6.QtWidgets import QApplication

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from src.core.signals.log_signals import LogSignals
from src.gui.pages.debugs.logs import LogsWidget
from src.gui.pages.debugs.logs_table import LogsTable
from src.gui.pages.debugs.message_table import MessageTable
from src.gui.pages.farmer.bank_tab import BankTab
from src.gui.pages.farmer.inventory_tab import InventoryTab
from src.protocol.message import MessageInfo
from src.services.logging_utils.log_level import LogLevel


class DebugLiveViewsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    @staticmethod
    def wait_for_batch() -> None:
        loop = QEventLoop()
        QTimer.singleShot(200, loop.quit)
        loop.exec()

    def test_logs_widget_keeps_capture_enabled_while_hidden(self) -> None:
        global_signals = LogSignals()
        bot_signals = LogSignals()
        widget = LogsWidget(global_signals, bot_signals)

        global_signals.publish(LogLevel.INFO, "global while hidden", datetime.now())
        bot_signals.publish(LogLevel.INFO, "bot while hidden", datetime.now())
        self.wait_for_batch()
        self.assertEqual(widget.logs_table.text_view.toPlainText(), "")

        widget.show()
        self.wait_for_batch()
        text = widget.logs_table.text_view.toPlainText()
        self.assertIn("global while hidden", text)
        self.assertIn("bot while hidden", text)

        widget.set_capture_enabled(False)
        bot_signals.publish(LogLevel.INFO, "discarded while paused", datetime.now())
        self.wait_for_batch()
        self.assertNotIn("discarded while paused", widget.logs_table.text_view.toPlainText())

    def test_message_table_filters_nested_content_and_retains_detail_payload(self) -> None:
        table = MessageTable()
        message = MessageInfo(
            received_time=datetime.now(),
            from_server=True,
            sub_msg_name="GameMapMovementMessage",
            msg_json={"actor": {"name": "Bouftou"}},
            obf_msg_json={"a": 1},
        )

        table.add_row(message, False)
        self.wait_for_batch()
        self.assertEqual(table.message_model.rowCount(), 0)

        table.set_updates_active(True)
        self.wait_for_batch()

        self.assertEqual(table.message_model.rowCount(), 1)
        detail = table.message_model.data(table.message_model.index(0, 3), Qt.ItemDataRole.UserRole)
        self.assertIs(detail, message)

        table.table.proxy_model.set_filters(["", "", "", "bouftou"])
        self.assertEqual(table.table.proxy_model.rowCount(), 1)
        table.table.proxy_model.set_filters(["", "", "", "absent"])
        self.assertEqual(table.table.proxy_model.rowCount(), 0)

    def test_logs_table_batches_plain_text_and_supports_search(self) -> None:
        table = LogsTable()
        table.add_row(LogLevel.WARNING, "Inventory almost full")
        self.wait_for_batch()
        self.assertEqual(table.text_view.toPlainText(), "")

        table.set_updates_active(True)
        self.wait_for_batch()

        self.assertIn("WARNING | Inventory almost full", table.text_view.toPlainText())
        table.search_edit.setText("Inventory")
        table.find_next()
        self.assertEqual(table.text_view.textCursor().selectedText(), "Inventory")

    def test_hidden_inventory_and_bank_keep_current_data_without_rendering(self) -> None:
        bot = MagicMock()
        inventory = InventoryTab(bot)
        bank = BankTab(bot)
        item = ObjectItemInventory(item=ObjectItem(uid=42, gid=1, quantity=3), position=63)

        inventory.on_added_object_item(item)
        bank.on_bank_refreshed([item])
        self.wait_for_batch()

        self.assertIs(inventory.items_by_uid[42], item)
        self.assertIs(bank.items_by_uid[42], item)
        self.assertEqual(inventory.list_widget.count(), 0)
        self.assertEqual(bank.list_widget.count(), 0)

        inventory.show()
        bank.show()
        self.wait_for_batch()

        self.assertEqual(inventory.list_widget.count(), 1)
        self.assertEqual(bank.list_widget.count(), 1)


if __name__ == "__main__":
    unittest.main()
