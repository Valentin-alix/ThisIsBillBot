import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator
from urllib.parse import unquote, urlparse

from playwright.async_api import BrowserContext, Error, ProxySettings, async_playwright

from ankama_launcher_emulator.consts import DEBUG_TRACES_DIR
from src.core.config import DEBUG
from src.utils.runtime_support import RuntimeSetupError, configure_browser_path
from src.services.install_validation import browser_repair_message

BROWSER_ARGS = ["--no-sandbox", "--disable-blink-features=AutomationControlled", "--window-position=0,0"]
_TRACE_RETENTION_DAYS = 7
_MAX_TRACE_DIRECTORIES = 5


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


def _trace_directory() -> Path:
    path = DEBUG_TRACES_DIR / f"{datetime.now():%Y%m%d_%H%M%S_%f}"
    path.mkdir(parents=True, exist_ok=False)
    _prune_expired_trace_directories(path)
    return path


def _prune_expired_trace_directories(active_trace_directory: Path) -> None:
    expiration_timestamp = (datetime.now() - timedelta(days=_TRACE_RETENTION_DAYS)).timestamp()
    trace_directories = [
        trace_directory
        for trace_directory in DEBUG_TRACES_DIR.iterdir()
        if trace_directory != active_trace_directory and trace_directory.is_dir()
    ]
    for trace_directory in trace_directories:
        if trace_directory.stat().st_mtime < expiration_timestamp:
            shutil.rmtree(trace_directory)
    recent_trace_directories = sorted(
        (trace_directory for trace_directory in trace_directories if trace_directory.exists()),
        key=lambda trace_directory: trace_directory.stat().st_mtime,
        reverse=True,
    )
    for trace_directory in recent_trace_directories[_MAX_TRACE_DIRECTORIES - 1 :]:
        shutil.rmtree(trace_directory)


@asynccontextmanager
async def launch_browser_context(
    *,
    proxy_url: str | None,
) -> AsyncGenerator[BrowserContext, None]:
    configure_browser_path()
    trace_directory = _trace_directory() if DEBUG else None
    proxy_settings = _playwright_proxy_settings(proxy_url)
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(
                traces_dir=trace_directory,
                channel="chromium",
                args=BROWSER_ARGS,
                proxy=proxy_settings,
            )
        except Error as error:
            raise RuntimeSetupError(browser_repair_message()) from error
        try:
            context = await browser.new_context(
                color_scheme="dark",
                viewport={"width": 1280, "height": 720},
                locale="fr-FR",
                timezone_id="Europe/Paris",
            )
            if trace_directory is not None:
                await context.tracing.start(name="session", screenshots=True, snapshots=True, sources=True)
            try:
                yield context
            finally:
                if trace_directory is not None:
                    await context.tracing.stop(path=trace_directory / "trace.zip")
        finally:
            await browser.close()
