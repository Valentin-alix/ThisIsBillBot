import re

from PyQt6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)


_NUMBER_PATTERN = re.compile(r"\b\d+\b")
_BRACKET_PATTERN = re.compile(r"[\[\]\(\)\{\}]")
_ID_PATTERN = re.compile(r"\b(?:gid|uid|id|tab|map_id)[:=]\s*\d+")
_KEYWORDS = [
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
    "CRITICAL",
    "failed",
    "success",
    "finished",
]
_KEYWORD_PATTERNS = [re.compile(r"\b" + keyword + r"\b", re.IGNORECASE) for keyword in _KEYWORDS]


class LogSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument | None = None) -> None:
        super().__init__(document)

        self.default_format = QTextCharFormat()
        self.default_format.setForeground(QColor("#D4D4D4"))

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#569CD6"))

        self.bracket_format = QTextCharFormat()
        self.bracket_format.setForeground(QColor("#808080"))

        self.id_format = QTextCharFormat()
        self.id_format.setForeground(QColor("#4EC9B0"))

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#C586C0"))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

    def highlightBlock(self, text: str | None):
        if text is None:
            return
        self.setFormat(0, len(text), self.default_format)
        for match in _NUMBER_PATTERN.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)

        for match in _BRACKET_PATTERN.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.bracket_format)

        for match in _ID_PATTERN.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.id_format)

        for pattern in _KEYWORD_PATTERNS:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.keyword_format)
