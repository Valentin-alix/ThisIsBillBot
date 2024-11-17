import threading
from collections import defaultdict

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget

from src.core.signals.shared_farm_signals import SharedSignals


class ThreadMonitorWidget(QWidget):
    def __init__(self, shared_signals: SharedSignals):
        super().__init__()
        self.shared_signals = shared_signals
        self.bot_manager_thread_count = 0
        self.warning_threshold = 30

        self.shared_signals.thread_count_update.connect(self._on_thread_count_update)

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(8)

        self.card = CardWidget()
        self.card.setLayout(QVBoxLayout())
        self.card.layout().setContentsMargins(16, 16, 16, 16)
        self.card.layout().setSpacing(8)
        self.layout().addWidget(self.card)

        self.total_threads_label = BodyLabel("Total threads: 0")
        self.card.layout().addWidget(self.total_threads_label)

        self.bot_threads_label = BodyLabel("Bot manager threads: 0")
        self.card.layout().addWidget(self.bot_threads_label)

        self.warning_label = BodyLabel("")
        self.warning_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        self.warning_label.hide()
        self.card.layout().addWidget(self.warning_label)

        self.thread_details_container = QWidget()
        self.thread_details_container.setLayout(QVBoxLayout())
        self.thread_details_container.layout().setContentsMargins(0, 8, 0, 0)
        self.thread_details_container.layout().setSpacing(4)
        self.card.layout().addWidget(self.thread_details_container)

        self._timer = QTimer()
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self._update_thread_count)
        self._timer.start()

        self._update_thread_count()

    def _on_thread_count_update(self, count: int):
        self.bot_manager_thread_count = count

    def _update_thread_count(self):
        total_thread_count = threading.active_count()

        self.total_threads_label.setText(f"Total threads: {total_thread_count}")

        if self.bot_manager_thread_count > 0:
            self.bot_threads_label.setText(
                f"Bot manager threads: {self.bot_manager_thread_count}"
            )
            self.bot_threads_label.show()
        else:
            self.bot_threads_label.hide()

        if total_thread_count > self.warning_threshold:
            self.warning_label.setText(
                f"WARNING: Thread count exceeds threshold ({self.warning_threshold})"
            )
            self.warning_label.show()
            self.card.setStyleSheet("border: 2px solid #ff6b6b;")
        else:
            self.warning_label.hide()
            self.card.setStyleSheet("")

        self._update_thread_details()

    def _update_thread_details(self):
        while self.thread_details_container.layout().count():
            child = self.thread_details_container.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        all_threads = threading.enumerate()
        count_by_thread_type: defaultdict[str, int] = defaultdict(int)
        for thread in all_threads:
            thread_name = thread.name
            thread_type = (
                thread_name.split("-")[0] if "-" in thread_name else thread_name
            )
            count_by_thread_type[thread_type] += 1

        for thread_type, count in sorted(
            count_by_thread_type.items(), key=lambda x: x[1], reverse=True
        ):
            row = QWidget()
            layout = QHBoxLayout()
            row.setLayout(layout)
            row.layout().setContentsMargins(0, 0, 0, 0)
            row.layout().setSpacing(8)

            name_label = BodyLabel(f"{thread_type}:")
            row.layout().addWidget(name_label)

            count_label = BodyLabel(f"{count}")
            row.layout().addWidget(count_label)

            layout.addStretch()

            self.thread_details_container.layout().addWidget(row)

    def cleanup(self):
        if self._timer.isActive():
            self._timer.stop()
