from types import SimpleNamespace
from urllib.parse import urlparse

import psutil
from nicegui import ui

from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.internet_utils import (
    get_available_network_interfaces,
)
from ankama_launcher_emulator.proxy.proxy_listener import (
    ProxyListener,
)
from ankama_launcher_emulator.server.handler import (
    AnkamaLauncherHandler,
)
from ankama_launcher_emulator.server.server import (
    AnkamaLauncherServer,
)


def _validation_proxy_url(proxy_url: str | None):
    if not proxy_url:
        return True
    parsed = urlparse(proxy_url)
    return parsed.scheme == "socks5"


def _build_proxy_listener(proxy_url: str | None) -> tuple[ProxyListener, str | None]:
    if not proxy_url:
        return ProxyListener(), None
    parsed = urlparse(proxy_url)
    if parsed.scheme == "socks5":
        return ProxyListener(
            socks5_host=parsed.hostname,
            socks5_port=parsed.port,
            socks5_username=parsed.username or None,
            socks5_password=parsed.password or None,
        ), None
    else:
        raise ValueError("Invalid proxy url")


def run_gui() -> None:
    handler = AnkamaLauncherHandler()
    server = AnkamaLauncherServer(handler)
    server.start()

    accounts = CryptoHelper.getStoredApiKeys()
    interfaces = get_available_network_interfaces()

    all_interface = {"Empty": None} | interfaces
    all_interface = {value: key for key, value in all_interface.items()}

    launched_pids: dict[str, int] = {}
    states: dict[str, SimpleNamespace] = {
        account["apikey"]["login"]: SimpleNamespace(running=False)
        for account in accounts
    }

    @ui.page("/")
    def index():  # pyright: ignore[reportUnusedFunction]
        ui.label("Ankama Launcher").classes("text-2xl font-bold mb-4")

        if not accounts:
            ui.label("No stored accounts found.").classes("text-red-500")
            return

        cards: dict[str, ui.card] = {}
        btns: dict[str, ui.button] = {}

        def _set_running(_card: ui.card, _btn: ui.button) -> None:
            _card.classes(add="border-green-500", remove="border-gray-600")
            _btn.set_text("Stop")
            _btn.classes(add="bg-red-600", remove="bg-blue-600")

        def _set_stopped(_card: ui.card, _btn: ui.button) -> None:
            _card.classes(add="border-gray-600", remove="border-green-500")
            _btn.set_text("Launch")
            _btn.classes(add="bg-blue-600", remove="bg-red-600")

        for account in accounts:
            login = account["apikey"]["login"]

            card = ui.card().classes("w-full mb-1 border-l-4 border-gray-600")
            cards[login] = card
            with card:
                with ui.row().classes("items-center gap-4 w-full"):
                    ui.label(login).classes("font-mono flex-1")

                    ip_select = ui.select(
                        options=all_interface,
                        label="Local interface",
                    ).classes("w-56")

                    proxy_input = ui.input(
                        label="Proxy URL (socks5://user:pass@host:port)",
                        validation={"Proxy URL not valid": _validation_proxy_url},
                    ).classes("w-128")

                    btn = ui.button("Launch").classes("bg-blue-600 text-white w-24")
                    btns[login] = btn

                    def on_click(
                        _login: str = login,
                        _card: ui.card = card,
                        _btn: ui.button = btn,
                        _ip_select: ui.select = ip_select,
                        _proxy_input: ui.input = proxy_input,
                        _state: SimpleNamespace = states[login],
                    ):
                        if _state.running:
                            pid = launched_pids.get(_login)
                            if pid and psutil.pid_exists(pid):
                                psutil.Process(pid).terminate()
                            launched_pids.pop(_login, None)
                            _state.running = False
                            _set_stopped(_card, _btn)
                        else:
                            _state.running = True
                            _set_running(_card, _btn)
                            try:
                                source_ip: str | None = _ip_select.value or None
                                raw_proxy = _proxy_input.value.strip() or None
                                proxy_listener, proxy_url = _build_proxy_listener(
                                    raw_proxy
                                )
                                pid = server.launch_dofus(
                                    _login,
                                    proxy_listener=proxy_listener,
                                    proxy_url=proxy_url,
                                    source_ip=source_ip,
                                )
                                launched_pids[_login] = pid
                                ui.notify(f"Launched {_login}", type="positive")
                            except Exception as e:
                                _state.running = False
                                _set_stopped(_card, _btn)
                                ui.notify(
                                    f"Failed to launch {_login}: {e}", type="negative"
                                )

                    btn.on_click(on_click)

        def check_processes():
            for login, pid in list(launched_pids.items()):
                if not psutil.pid_exists(pid):
                    del launched_pids[login]
                    states[login].running = False
                    _set_stopped(cards[login], btns[login])
                    ui.notify(f"{login} stopped", type="warning")

        ui.timer(2.0, check_processes)

    ui.run(title="Ankama Launcher", port=8081, reload=False, dark=True)
