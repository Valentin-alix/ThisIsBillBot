from urllib.parse import urlparse

from ankama_launcher_emulator.proxy.dofus3.proxy_listener import BaseProxyListener


def validation_proxy_url(proxy_url: str | None) -> bool:
    if not proxy_url:
        return True
    return urlparse(proxy_url).scheme == "socks5"


def get_info_by_proxy_url(proxy_url: str):
    parsed = urlparse(proxy_url)
    if parsed.scheme != "socks5":
        raise ValueError("Invalid proxy url")
    return parsed


def build_proxy_listener(proxy_url: str | None) -> tuple[BaseProxyListener, str | None]:
    if not proxy_url:
        return BaseProxyListener(), None
    parsed = get_info_by_proxy_url(proxy_url)
    return BaseProxyListener(
        socks5_host=parsed.hostname,
        socks5_port=parsed.port,
        socks5_username=parsed.username or None,
        socks5_password=parsed.password or None,
    ), None
