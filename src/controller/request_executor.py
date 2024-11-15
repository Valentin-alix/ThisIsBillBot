from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

from httpx import ConnectTimeout, ReadTimeout

from src.controller.scraping_d3_client.scraping_d3_client.models.http_validation_error import (
    HTTPValidationError,
)

T = TypeVar("T")


class RequestExecutor:
    def __init__(self):
        self.executor = ThreadPoolExecutor()

    def run_with_callback(
        self,
        func: Callable[..., T],
        callback: Callable[[T | HTTPValidationError], Any] | None = None,
    ) -> None:
        def silence_connect_timeout(func: Callable[..., T | HTTPValidationError]):
            try:
                return func()
            except (ConnectTimeout, ReadTimeout):
                return HTTPValidationError()

        future = self.executor.submit(lambda: silence_connect_timeout(func))
        if callback:
            future.add_done_callback(lambda _func: callback(_func.result()))
