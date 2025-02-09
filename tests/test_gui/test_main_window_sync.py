import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.gui.main_window import MainWindow


class MainWindowSynchronizeBotsTests(unittest.TestCase):
    def test_remove_account_removes_gui_references(self) -> None:
        account_widget = SimpleNamespace(
            objectName=MagicMock(return_value="alice"),
            deleteLater=MagicMock(),
        )
        next_widget = SimpleNamespace(objectName=MagicMock(return_value="bob"))
        window = SimpleNamespace(
            bots_by_login={"alice": MagicMock(), "bob": MagicMock()},
            account_widgets=[account_widget, next_widget],
            removeWidget=MagicMock(),
            switchTo=MagicMock(),
            navigationInterface=SimpleNamespace(setCurrentItem=MagicMock()),
        )
        bot = SimpleNamespace(account={"apikey": {"login": "alice"}})

        MainWindow.remove_account(window, bot)  # type: ignore[arg-type]

        self.assertNotIn("alice", window.bots_by_login)
        self.assertEqual(window.account_widgets, [next_widget])
        window.removeWidget.assert_called_once_with("alice", account_widget)
        account_widget.deleteLater.assert_called_once_with()
        window.switchTo.assert_called_once_with(next_widget)
        window.navigationInterface.setCurrentItem.assert_called_once_with("bob")


if __name__ == "__main__":
    unittest.main()
