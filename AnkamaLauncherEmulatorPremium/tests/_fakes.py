from unittest.mock import AsyncMock, MagicMock

from ankama_launcher_emulator_premium.web._client.mailbox import MailboxSettings


class FakeBrowserContext:
    """Fake async context manager standing in for launch_browser_context() in tests."""

    def __init__(self, page: MagicMock) -> None:
        self.new_page = AsyncMock(return_value=page)

    async def __aenter__(self) -> "FakeBrowserContext":
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: object | None,
    ) -> None:
        return None


class FakeLocator:
    """Fake Playwright Locator exposing only the methods exercised by these tests."""

    def __init__(self, count: int, *, visible: bool = True) -> None:
        self._count = count
        self._visible = visible
        self.fill = AsyncMock()
        self.click = AsyncMock()
        self.wait_for = AsyncMock()

    @property
    def first(self) -> "FakeLocator":
        return self

    async def count(self) -> int:
        return self._count

    async def is_visible(self) -> bool:
        return self._visible

    def set_count(self, count: int) -> None:
        self._count = count


def mailbox_settings() -> MailboxSettings:
    return MailboxSettings(host="imap.test", username="u", password="p")
