from typing import TYPE_CHECKING
from urllib.parse import quote, urlparse

from pydantic import BaseModel

if TYPE_CHECKING:
    from ankama_launcher_emulator_premium.proxy.dofus3.proxy_listener import (
        ProxyListener,
    )


class ProxyConfig(BaseModel):
    rejected: bool = False
    host: str
    http_port: int
    socks_port: int
    username: str
    password: str


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


def validation_proxy_url(proxy_url: str | None) -> bool:
    if not proxy_url:
        return True
    return urlparse(proxy_url).scheme == "socks5"


def validate_proxy_url(proxy_url: str | None) -> str | None:
    if proxy_url is None:
        return None
    parsed = urlparse(proxy_url)
    if parsed.scheme != "socks5" or not parsed.hostname or parsed.port is None:
        raise ValueError("proxy_url must be a socks5://host:port URL")
    return proxy_url


def get_info_by_proxy_url(proxy_url: str):
    parsed = urlparse(proxy_url)
    if parsed.scheme != "socks5":
        raise ValueError("Invalid proxy url")
    return parsed


def build_proxy_listener(proxy_url: str | None) -> tuple["ProxyListener", str | None]:
    from ankama_launcher_emulator_premium.proxy.dofus3.proxy_listener import (
        ProxyListener,
    )

    if not proxy_url:
        return ProxyListener(), None
    get_info_by_proxy_url(proxy_url)
    return ProxyListener(), proxy_url
