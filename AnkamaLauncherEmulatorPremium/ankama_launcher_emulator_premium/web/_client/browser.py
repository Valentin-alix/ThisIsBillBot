from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import unquote, urlparse

from playwright.async_api import BrowserContext, ProxySettings, async_playwright

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.user_agent import CHROME_USER_AGENT

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--window-position=-1920,0",
]


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


@asynccontextmanager
async def launch_browser_context(
    *, headless: bool, proxy_url: str | None, channel: str | None = None
) -> AsyncIterator[BrowserContext]:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless, channel=channel, args=BROWSER_ARGS)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=CHROME_USER_AGENT,
            proxy=_playwright_proxy_settings(proxy_url),
            locale="fr-FR",
            timezone_id="Europe/Paris",
            extra_http_headers={
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
        )
        try:
            yield context
        finally:
            await browser.close()
