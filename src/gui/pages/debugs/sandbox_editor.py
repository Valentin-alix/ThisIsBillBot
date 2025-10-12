import ast
import logging
import re
from collections.abc import Callable

from PyQt6.Qsci import QsciLexerPython, QsciScintilla
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QWidget
from pyflakes.checker import Checker

from src.services.sandbox.completions import get_completions

logger = logging.getLogger()

_TRIGGER_CHARS = {"."}
_PREFIX_PATTERN = re.compile(r"[\w]*$")
_ERROR_MARKER = 0


class SandboxCodeEdit(QsciScintilla):
    syntax_error_changed = pyqtSignal(object)

    def __init__(
        self,
        namespace_provider: Callable[[], dict[str, object]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._namespace_provider = namespace_provider

        self._configure_editor()
        self._configure_lexer()

        self._syntax_timer = QTimer(self)
        self._syntax_timer.setSingleShot(True)
        self._syntax_timer.setInterval(300)
        self._syntax_timer.timeout.connect(self._check_syntax)

        self.textChanged.connect(self._on_text_changed)
        self.SCN_CHARADDED.connect(self._on_char_added)

    def _configure_editor(self) -> None:
        self.setUtf8(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(1, 14)
        self.markerDefine(QsciScintilla.MarkerSymbol.Circle, _ERROR_MARKER)
        self.setMarkerBackgroundColor(QColor("#E51400"), _ERROR_MARKER)

        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsNone)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionReplaceWord(True)

    def _configure_lexer(self) -> None:
        lexer = QsciLexerPython(self)
        font = QFont("Consolas", 10)
        lexer.setFont(font)

        paper = QColor("#1E1E1E")
        default_fg = QColor("#D4D4D4")
        keyword_fg = QColor("#C586C0")
        string_fg = QColor("#CE9178")
        number_fg = QColor("#569CD6")
        comment_fg = QColor("#6A9955")
        function_fg = QColor("#4EC9B0")

        lexer.setDefaultPaper(paper)
        lexer.setDefaultColor(default_fg)
        lexer.setPaper(paper)
        lexer.setColor(default_fg)
        lexer.setColor(keyword_fg, QsciLexerPython.Keyword)
        lexer.setColor(string_fg, QsciLexerPython.DoubleQuotedString)
        lexer.setColor(string_fg, QsciLexerPython.SingleQuotedString)
        lexer.setColor(string_fg, QsciLexerPython.TripleDoubleQuotedString)
        lexer.setColor(string_fg, QsciLexerPython.TripleSingleQuotedString)
        lexer.setColor(number_fg, QsciLexerPython.Number)
        lexer.setColor(comment_fg, QsciLexerPython.Comment)
        lexer.setColor(function_fg, QsciLexerPython.FunctionMethodName)
        lexer.setColor(function_fg, QsciLexerPython.ClassName)

        self.setLexer(lexer)
        self.setCaretForegroundColor(default_fg)
        self.setMarginsBackgroundColor(paper)
        self.setMarginsForegroundColor(comment_fg)

    def _on_text_changed(self) -> None:
        self._syntax_timer.start()

    def _on_char_added(self, char_code: int) -> None:
        char = chr(char_code)
        if char.isalnum() or char == "_" or char in _TRIGGER_CHARS:
            self._update_completions()
        else:
            self.cancelList()

    def _update_completions(self) -> None:
        cursor_line, cursor_index = self.getCursorPosition()

        try:
            namespace = self._namespace_provider()
            completions = get_completions(self.text(), cursor_line + 1, cursor_index, namespace)
        except Exception:
            logger.exception("Sandbox completion failed")
            completions = []

        if not completions:
            self.cancelList()
            return

        text_before_cursor = self.text(cursor_line)[:cursor_index]
        prefix_match = _PREFIX_PATTERN.search(text_before_cursor)
        prefix_len = len(prefix_match.group()) if prefix_match else 0

        names = sorted(
            (completion.name for completion in completions),
            key=lambda name: (name.startswith("_"), name.startswith("__"), name.lower()),
        )
        self.SendScintilla(QsciScintilla.SCI_AUTOCSHOW, prefix_len, " ".join(names).encode("utf-8"))

    def _check_syntax(self) -> None:
        self.markerDeleteAll(_ERROR_MARKER)
        code = self.text()
        if not code.strip():
            self.syntax_error_changed.emit(None)
            return

        try:
            tree = ast.parse(code)
        except SyntaxError as error:
            if error.lineno is not None:
                self.markerAdd(error.lineno - 1, _ERROR_MARKER)
            self.syntax_error_changed.emit(f"Ligne {error.lineno}: {error.msg}")
            return

        try:
            namespace = self._namespace_provider()
        except Exception:
            logger.exception("Sandbox namespace build failed")
            namespace = {}

        messages = Checker(tree, builtins=list(namespace)).messages
        if not messages:
            self.syntax_error_changed.emit(None)
            return

        for message in messages:
            self.markerAdd(message.lineno - 1, _ERROR_MARKER)

        first = messages[0]
        first_text = first.message % first.message_args
        suffix = f" (+{len(messages) - 1} autres)" if len(messages) > 1 else ""
        self.syntax_error_changed.emit(f"Ligne {first.lineno}: {first_text}{suffix}")
