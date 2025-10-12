import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy, QSplitter, QTextEdit, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, PrimaryPushButton

from src.services.background import run_in_background
from src.core.bot.bot import Bot
from src.gui.pages.debugs.sandbox_editor import SandboxCodeEdit
from src.services.sandbox.executor import SandboxExecutor, SandboxResult


class SandboxWidget(QWidget):
    def __init__(self, bot: Bot, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.bot = bot

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)

        self.run_btn = PrimaryPushButton(FluentIcon.PLAY, "Exécuter", self)
        self.run_btn.clicked.connect(self.on_run)
        layout.addWidget(self.run_btn)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.code_edit = SandboxCodeEdit(
            namespace_provider=lambda: SandboxExecutor(bot=self.bot).build_namespace(),
            parent=splitter,
        )
        self.code_edit.syntax_error_changed.connect(self._on_syntax_error_changed)
        self.code_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.addWidget(self.code_edit)

        self.syntax_error_label = QLabel(self)
        self.syntax_error_label.setStyleSheet("color: #E51400;")
        self.syntax_error_label.hide()
        layout.addWidget(self.syntax_error_label)

        self.output_view = QTextEdit(splitter)
        self.output_view.setReadOnly(True)
        self.output_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.addWidget(self.output_view)

    def _on_syntax_error_changed(self, message: str | None) -> None:
        self.syntax_error_label.setText(message or "")
        self.syntax_error_label.setVisible(message is not None)

    def on_run(self) -> None:
        code = self.code_edit.text()
        if not code.strip():
            return
        self.run_btn.setEnabled(False)
        executor = SandboxExecutor(bot=self.bot)
        run_in_background(
            lambda _progress: executor.run(code),
            on_success=lambda result: self._append_output(code, result),
            on_error=lambda error: self._append_error(code, error),
        )

    def _append_output(self, code: str, result: SandboxResult) -> None:
        self.run_btn.setEnabled(True)
        lines = [f"[{datetime.datetime.now():%H:%M:%S}] >>> {code}"]
        if result.stdout:
            lines.append(result.stdout.rstrip("\n"))
        if result.result_repr is not None:
            lines.append(result.result_repr)
        if result.error is not None:
            lines.append(result.error.rstrip("\n"))
        self.output_view.append("\n".join(lines))

    def _append_error(self, code: str, error: object) -> None:
        self.run_btn.setEnabled(True)
        self.output_view.append(f"[{datetime.datetime.now():%H:%M:%S}] >>> {code}\n{error}")
