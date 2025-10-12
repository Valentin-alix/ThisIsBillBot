from urllib.parse import quote, urlparse

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.schedule_profile import (
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
