import inspect

from PyQt6.QtWidgets import QTextEdit, QWidget
from qfluentwidgets import MessageBoxBase, PushButton, SubtitleLabel

from src.core.events_manager.listener import Listener


class ListenerDetailsBox(MessageBoxBase):
    def __init__(self, listener: Listener, parent: QWidget):
        super().__init__(parent=parent)
        self.title_label = SubtitleLabel("Listener Details", parent=self)
        originator_name = listener.originator.__class__.__name__
        msg_type_name = listener.msg_type.__name__
        registered_at_str = listener.registered_at.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        timeout_str = str(listener.timeout) if listener.timeout else "None"

        header_text = f"""
        Originator: {originator_name}
        Message Type: {msg_type_name}
        Priority: {listener.priority}
        Once: {"Yes" if listener.once else "No"}
        Registered At: {registered_at_str}
        Timeout: {timeout_str}

        Callback Source:
                        """
        if hasattr(listener.callback, "func"):
            source = inspect.getsource(listener.callback.func)  # pyright: ignore[reportFunctionMemberAccess]
        else:
            source = inspect.getsource(listener.callback)
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

        self.details_edit.setMinimumHeight(400)
        self.details_edit.setMinimumWidth(600)

        self.close_button = PushButton("Close", self)
        self.close_button.clicked.connect(self.reject)

        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.details_edit)
        self.viewLayout.addWidget(self.close_button)
