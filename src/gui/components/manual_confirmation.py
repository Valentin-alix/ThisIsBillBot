from PyQt6.QtCore import QObject, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, LineEdit, isDarkTheme

from src.services.manual_confirmation import ConfirmationRequest, manual_confirmation


class ManualConfirmationDialogs(QObject):
    requested = pyqtSignal(object)
    closed = pyqtSignal(str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.window = parent
        self.dialogs: dict[str, QDialog] = {}
        self.requested.connect(self.open_request)
        self.closed.connect(self.close_request)
        manual_confirmation.install(self.requested.emit, self.closed.emit)

    def open_request(self, request: ConfirmationRequest) -> None:
        if not manual_confirmation.is_pending(request.identifier):
            return
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Confirmation code")
        dialog.setStyleSheet(
            "QDialog { background: #202020; }" if isDarkTheme() else "QDialog { background: white; }"
        )
        layout = QVBoxLayout(dialog)
        layout.addWidget(BodyLabel(f"Code received for {request.email}", dialog))
        code = LineEdit(dialog)
        code.setPlaceholderText("6 chiffres")
        code.setMaxLength(6)
        code.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{6}"), code))
        layout.addWidget(code)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog
        )
        ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        assert ok is not None
        ok.setEnabled(False)

        def on_text_changed(_text: str) -> None:
            ok.setEnabled(code.hasAcceptableInput())

        code.textChanged.connect(on_text_changed)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        def on_finished(result: int) -> None:
            manual_confirmation.submit(
                request.identifier, code.text() if result == QDialog.DialogCode.Accepted else None
            )

        dialog.finished.connect(on_finished)
        self.dialogs[request.identifier] = dialog
        dialog.show()
        code.setFocus()

    def close_request(self, identifier: str) -> None:
        dialog = self.dialogs.pop(identifier, None)
        if dialog is not None:
            dialog.reject()
            dialog.deleteLater()

    def shutdown(self) -> None:
        manual_confirmation.shutdown()
        for identifier in list(self.dialogs):
            self.close_request(identifier)
