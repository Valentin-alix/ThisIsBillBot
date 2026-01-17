import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator
from urllib.parse import unquote, urlparse

from playwright.async_api import BrowserContext, ProxySettings, async_playwright

from ankama_launcher_emulator_premium.consts import DEBUG_TRACES_DIR

BROWSER_ARGS = ["--no-sandbox", "--disable-blink-features=AutomationControlled", "--window-position=-3840,0"]
_TRACE_RETENTION_DAYS = 7


def _playwright_proxy_settings(proxy_url: str | None) -> ProxySettings | None:
    if proxy_url is None:
        return None
    parsed_proxy = urlparse(proxy_url)
    if parsed_proxy.hostname is None or parsed_proxy.port is None:
        raise ValueError("proxy_url must include a host and port")
    server = f"{parsed_proxy.scheme}://{parsed_proxy.hostname}:{parsed_proxy.port}"
    proxy_settings: ProxySettings = {"server": server}
    if parsed_proxy.username is not None:
        proxy_settings["username"] = unquote(parsed_proxy.username)
    if parsed_proxy.password is not None:
        proxy_settings["password"] = unquote(parsed_proxy.password)
    return proxy_settings


def _trace_directory(login: str) -> Path:
    safe_login = "".join(char if char.isalnum() or char in ".@_-" else "_" for char in login)
    path = DEBUG_TRACES_DIR / f"{datetime.now():%Y%m%d_%H%M%S_%f}_{safe_login}"
    path.mkdir(parents=True, exist_ok=False)
    _prune_expired_trace_directories(path)
    return path


def _prune_expired_trace_directories(active_trace_directory: Path) -> None:
    expiration_timestamp = (datetime.now() - timedelta(days=_TRACE_RETENTION_DAYS)).timestamp()
    for trace_directory in DEBUG_TRACES_DIR.iterdir():
        if (
            trace_directory != active_trace_directory
            and trace_directory.is_dir()
            and trace_directory.stat().st_mtime < expiration_timestamp
        ):
            shutil.rmtree(trace_directory)


@asynccontextmanager
async def launch_browser_context(
    *, login: str, proxy_url: str | None, headless: bool = False
) -> AsyncGenerator[BrowserContext, None]:
    trace_directory = _trace_directory(login)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=headless,
            traces_dir=trace_directory,
            channel="chromium",
            args=BROWSER_ARGS,
            proxy=_playwright_proxy_settings(proxy_url),
        )
        context = await browser.new_context(
            color_scheme="dark",
            viewport={"width": 1280, "height": 720},
            locale="fr-FR",
            timezone_id="Europe/Paris",
        )
        await context.tracing.start(name="session", screenshots=True, snapshots=True, sources=True)
        try:
            yield context
        finally:
            await context.tracing.stop(path=trace_directory / "trace.zip")
            await browser.close()
