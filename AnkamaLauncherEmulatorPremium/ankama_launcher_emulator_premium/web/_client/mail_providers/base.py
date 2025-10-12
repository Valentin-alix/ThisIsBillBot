from datetime import datetime
from typing import Protocol


class MailboxCodeTimeoutError(TimeoutError):
    pass


class MailCodeProvider(Protocol):
    async def wait_for_code(self, *, since: datetime, timeout_seconds: int) -> str | None: ...
