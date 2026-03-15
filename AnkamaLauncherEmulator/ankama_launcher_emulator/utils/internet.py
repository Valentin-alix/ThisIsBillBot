import logging
import socket
from collections.abc import Callable
from functools import wraps
from time import sleep
from typing import Any, ParamSpec, TypeVar

import requests

from ankama_launcher_emulator.exceptions import HaapiHttpError

logger = logging.getLogger()
ParamT = ParamSpec("ParamT")
ReturnT = TypeVar("ReturnT")


def raise_for_status_with_content(response: requests.Response) -> Any:
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        error_msg = f"HTTP Error: {err} - Response: {response.text}"
        raise HaapiHttpError(error_msg, response.status_code) from err


def retry_internet(
    func: Callable[ParamT, ReturnT],
) -> Callable[ParamT, ReturnT]:
    @wraps(func)
    def wrapper(*args: ParamT.args, **kwargs: ParamT.kwargs) -> ReturnT:
        try_count: int = 3
        while try_count > 0:
            try:
                return func(*args, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                socket.gaierror,
            ) as err:
                logger.info(f"[NETWORK] Error: {err}. Retrying…")
            try_count -= 1
            if try_count > 0:
                sleep(10)
        raise requests.exceptions.ConnectionError

    return wrapper
