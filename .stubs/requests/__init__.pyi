from collections.abc import Mapping

from .adapters import HTTPAdapter


class HTTPError(Exception): ...
class ConnectionError(Exception): ...
class Timeout(Exception): ...


class _Exceptions:
    HTTPError: type[HTTPError]
    ConnectionError: type[ConnectionError]
    Timeout: type[Timeout]


exceptions: _Exceptions


class Response:
    text: str
    def raise_for_status(self) -> None: ...
    def json(self) -> object: ...


class Session:
    proxies: dict[str, str]
    headers: dict[str, str]
    def __init__(self) -> None: ...
    def post(
        self,
        url: str,
        *,
        data: object = ...,
        json: object = ...,
        headers: dict[str, str] | None = ...,
        verify: bool = ...,
    ) -> Response: ...
    def get(
        self,
        url: str,
        *,
        params: Mapping[str, object] | None = ...,
        verify: bool = ...,
        timeout: float | int = ...,
    ) -> Response: ...
    def mount(self, prefix: str, adapter: HTTPAdapter) -> None: ...
