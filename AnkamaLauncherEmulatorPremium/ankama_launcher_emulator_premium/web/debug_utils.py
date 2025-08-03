"""Helpers for saving diagnostic HTML dumps to disk."""

import logging
from datetime import datetime
from pathlib import Path

from playwright._impl._errors import TargetClosedError
from playwright.async_api import Page

from ankama_launcher_emulator_premium.consts import DEBUG_DUMPS_DIR

logger = logging.getLogger(__name__)


def dump_html(label: str, html: str) -> Path:
    """Write *html* to the Premium debug directory and log the path."""
    DEBUG_DUMPS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = DEBUG_DUMPS_DIR / f"{label}_{ts}.html"
    path.write_text(html, encoding="utf-8")
    logger.info("HTML dump saved to %s", path)
    return path


async def dump_page_html(label: str, page: Page) -> Path:
    return dump_html(label, await page.content())


async def try_dump_page_html(label: str, page: Page, logger: logging.Logger, log_prefix: str) -> Path | None:
    try:
        return await dump_page_html(label, page)
    except TargetClosedError:
        logger.info("%s Browser page was already closed; skipping HTML dump.", log_prefix)
        return None
