import inspect
from collections.abc import Callable
from functools import partial
from typing import Any, cast

from google.protobuf.message import Message
from PyQt6.QtWidgets import QTextEdit, QWidget
from qfluentwidgets import MessageBoxBase, SubtitleLabel

from src.core.events_manager.listener import Listener


def _get_callback_source_target(
    callback: Callable[..., object],
) -> Callable[..., object]:
    if isinstance(callback, partial):
        return callback.func
    return callback


class ListenerDetailsBox(MessageBoxBase):
    def __init__(self, listener: Listener[Message], parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.title_label = SubtitleLabel("Listener details", parent=self)
        originator_name = listener.originator.__class__.__name__
        msg_type_name = listener.msg_type.__name__
        registered_at_str = listener.registered_at.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        timeout_str = str(listener.timeout) if listener.timeout else "None"

        header_text = f"""
        Origine : {originator_name}
        Message type: {msg_type_name}
        Priority: {listener.priority}
        One-time: {"Yes" if listener.once else "No"}
        Registered at: {registered_at_str}
        Timeout: {timeout_str}

        Callback source:
                        """
        source = inspect.getsource(_get_callback_source_target(listener.callback))
        highlighted_code = source
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    color: #D4D4D4;
                    font-family: Consolas, 'Courier New', monospace;
                    font-size: 9pt;
                }}
                pre {{
                    margin: 0;
                    padding: 0;
                }}
            </style>
        </head>
        <body>
            <pre>{header_text}</pre>
            <pre>{highlighted_code}</pre>
        </body>
        </html>
        """

        self.details_edit = QTextEdit(parent=self)
        self.details_edit.setReadOnly(True)
        self.details_edit.setHtml(html_content)
        self.details_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
            }
        """)

        self.details_edit.setMinimumWidth(600)

        message_box = cast(Any, self)
        message_box.hideYesButton()
        message_box.cancelButton.setText("Close")

        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.details_edit)
