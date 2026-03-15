import asyncio
import re
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from threading import RLock
from uuid import uuid4


@dataclass(frozen=True)
class ConfirmationRequest:
    identifier: str
    email: str


class ManualConfirmationBroker:
    def __init__(self) -> None:
        self._lock = RLock()
        self._pending: dict[str, Future[str | None]] = {}
        self._requested: Callable[[ConfirmationRequest], None] | None = None
        self._closed: Callable[[str], None] | None = None

    @property
    def enabled(self) -> bool:
        with self._lock:
            return self._requested is not None

    def install(
        self, requested: Callable[[ConfirmationRequest], None], closed: Callable[[str], None]
    ) -> None:
        with self._lock:
            self._requested = requested
            self._closed = closed

    def shutdown(self) -> None:
        with self._lock:
            self._requested = None
            for identifier in list(self._pending):
                self.submit(identifier, None)
            self._closed = None

    def is_pending(self, identifier: str) -> bool:
        with self._lock:
            return identifier in self._pending

    def submit(self, identifier: str, code: str | None) -> None:
        if code is not None and re.fullmatch(r"[0-9]{6}", code) is None:
            raise ValueError("The code must contain six digits.")
        with self._lock:
            future = self._pending.pop(identifier, None)
            if future is None:
                return
            if not future.done():
                future.set_result(code)
            if self._closed is not None:
                self._closed(identifier)

    async def wait(self, email: str, timeout_seconds: float) -> str | None:
        request = ConfirmationRequest(uuid4().hex, email)
        future: Future[str | None] = Future()
        with self._lock:
            if self._requested is None:
                return None
            self._pending[request.identifier] = future
            self._requested(request)
        try:
            return await asyncio.wait_for(asyncio.wrap_future(future), timeout_seconds)
        except TimeoutError:
            return None
        finally:
            self.submit(request.identifier, None)


manual_confirmation = ManualConfirmationBroker()
