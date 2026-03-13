from urllib.parse import quote, urlparse

from ankama_launcher_emulator.interfaces.schedule_profile import (
    ProxyConfig,
)


def _quote_proxy_part(value: str) -> str:
    return quote(value, safe="")


def build_http_proxy_url(proxy: ProxyConfig) -> str:
    username = _quote_proxy_part(proxy.username)
    password = _quote_proxy_part(proxy.password)
    return f"http://{username}:{password}@{proxy.host}:{proxy.http_port}"


def build_socks_proxy_url(proxy: ProxyConfig) -> str:
    username = _quote_proxy_part(proxy.username)
    password = _quote_proxy_part(proxy.password)
    return f"socks5://{username}:{password}@{proxy.host}:{proxy.socks_port}"


def get_info_by_proxy_url(proxy_url: str):
    parsed = urlparse(proxy_url)
    if parsed.scheme != "socks5":
        raise ValueError("Invalid proxy url")
    return parsed
