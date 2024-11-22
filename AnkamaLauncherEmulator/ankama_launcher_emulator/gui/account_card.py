import psutil
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel
from qfluentwidgets import BodyLabel, CardWidget, ComboBox, LineEdit, PrimaryPushButton

from ankama_launcher_emulator.gui.consts import GREEN_HEXA
from ankama_launcher_emulator.utils.proxy import validation_proxy_url


class AccountCard(CardWidget):
    launch_requested = pyqtSignal(
        object, object
    )  # (interface_ip: str | None, proxy_url: str | None)
    error_occurred = pyqtSignal(str)

    def __init__(
        self, login: str, all_interface: dict[str, tuple[str, str]], parent=None
    ):
        super().__init__(parent)
        self.login = login
        self._current_pid: int | None = None
        self._setup_ui(all_interface)

        self._monitor_timer = QTimer(self)
        self._monitor_timer.setInterval(1500)
        self._monitor_timer.timeout.connect(self._check_process)

    def _setup_ui(self, all_interface: dict[str, tuple[str, str]]) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self._status_dot = QLabel()
        self._status_dot.setFixedSize(10, 10)
        self._status_dot.setStyleSheet(
            f"background-color: {GREEN_HEXA}; border-radius: 5px;"
        )
        self._status_dot.setVisible(False)
        layout.addWidget(self._status_dot)

        layout.addWidget(BodyLabel(self.login), 1)

        self._ip_combo = ComboBox()
        self._ip_combo.addItem("Auto", userData=None)
        self._ip_combo.setFixedWidth(200)

        for ip_value, (display_name, public_ip) in all_interface.items():
            self._ip_combo.addItem(
                f"{display_name}\t{public_ip}",
                userData=ip_value,
            )
        layout.addWidget(self._ip_combo)

        self._proxy_input = LineEdit()
        self._proxy_input.setPlaceholderText("Proxy (socks5://user:pass@host:port)")
        self._proxy_input.setFixedWidth(300)
        layout.addWidget(self._proxy_input)

        self._launch_btn = PrimaryPushButton("Launch")
        self._launch_btn.setFixedWidth(100)
        self._launch_btn.clicked.connect(self._on_btn_clicked)
        layout.addWidget(self._launch_btn)

    def _on_btn_clicked(self) -> None:
        if self._current_pid is not None:
            self._stop_process()
        else:
            self._on_launch_clicked()

    def _on_launch_clicked(self) -> None:
        interface_ip = self._ip_combo.currentData() or None
        proxy_url = self._proxy_input.text().strip() or None

        if proxy_url and not validation_proxy_url(proxy_url):
            self.error_occurred.emit("Invalid proxy url")
            return

        self._launch_btn.setDisabled(True)
        self.launch_requested.emit(interface_ip, proxy_url)

    def _stop_process(self) -> None:
        if self._current_pid is None:
            return
        try:
            proc = psutil.Process(self._current_pid)
            children = proc.children(recursive=True)
            proc.terminate()
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def set_running(self, pid: int) -> None:
        self._current_pid = pid
        self._launch_btn.setText("Stop")
        self._launch_btn.setEnabled(True)
        self._status_dot.setVisible(True)
        self._monitor_timer.start()

    def _check_process(self) -> None:
        if self._current_pid is None:
            self._monitor_timer.stop()
            return
        try:
            proc = psutil.Process(self._current_pid)
            if not proc.is_running() or proc.status() == psutil.STATUS_ZOMBIE:
                self._on_process_ended()
        except psutil.NoSuchProcess:
            self._on_process_ended()

    def _on_process_ended(self) -> None:
        self._current_pid = None
        self._monitor_timer.stop()
        self._launch_btn.setText("Launch")
        self._launch_btn.setEnabled(True)
        self._status_dot.setVisible(False)

    def set_launch_enabled(self, enabled: bool) -> None:
        self._launch_btn.setEnabled(enabled)
