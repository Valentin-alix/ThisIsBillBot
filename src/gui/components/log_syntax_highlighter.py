import re

from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


class LogSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        number_pattern = re.compile(r"\b\d+\b")
        for match in number_pattern.finditer(text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.number_format
            )

        bracket_pattern = re.compile(r"[\[\]\(\)\{\}]")
        for match in bracket_pattern.finditer(text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.bracket_format
            )

        id_pattern = re.compile(r"\b(?:gid|uid|id|tab|map_id)[:=]\s*\d+")
        for match in id_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.id_format)

        keywords = [
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
            "CRITICAL",
            "failed",
            "success",
            "finished",
        ]
        for keyword in keywords:
            pattern = re.compile(r"\b" + keyword + r"\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                self.setFormat(
                    match.start(), match.end() - match.start(), self.keyword_format
                )
