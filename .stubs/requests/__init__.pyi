from collections.abc import Iterator, Mapping
from http.cookiejar import Cookie, CookieJar
from types import TracebackType
from typing import Any

from .adapters import HTTPAdapter

class RequestException(OSError): ...
class HTTPError(RequestException): ...
class ConnectionError(RequestException): ...
class Timeout(RequestException): ...

def get(
    url: str, *, timeout: float | int | tuple[float, float] = ...,
    headers: Mapping[str, str] | None = ..., stream: bool = ...,
) -> Response: ...

class _Exceptions:
    HTTPError: type[HTTPError]
    ConnectionError: type[ConnectionError]
    Timeout: type[Timeout]

exceptions: _Exceptions

class RequestsCookieJar(CookieJar):
    def set(
        self,
        name: str,
        value: str,
        *,
        domain: str = ...,
        path: str = ...,
    ) -> Cookie: ...
    def set_cookie(self, cookie: Cookie) -> None: ...

class _Cookies:
    def create_cookie(
        self, name: str, value: str, *, domain: str = ..., path: str = ...
    ) -> Cookie: ...

cookies: _Cookies

class Response:
    content: bytes
    text: str
    url: str
    status_code: int
    headers: dict[str, str]
    cookies: RequestsCookieJar
    def raise_for_status(self) -> None: ...
    def iter_content(self, chunk_size: int = ...) -> Iterator[bytes]: ...
    def json(self) -> Any: ...
    def __enter__(self) -> Response: ...
    def __exit__(
        self, exc_type: type[BaseException] | None,
        exc_value: BaseException | None, traceback: TracebackType | None,
    ) -> None: ...

class Session:
    proxies: dict[str, str]
    headers: dict[str, str]
    cookies: RequestsCookieJar
    def __init__(self) -> None: ...
    def post(
        self,
        url: str,
        *,
        data: object = ...,
        json: object = ...,
        headers: dict[str, str] | None = ...,
        verify: bool = ...,
        timeout: float | int = ...,
        allow_redirects: bool = ...,
    ) -> Response: ...
    def get(
        self,
        url: str,
        *,
        params: Mapping[str, object] | None = ...,
        verify: bool = ...,
        timeout: float | int = ...,
        allow_redirects: bool = ...,
    ) -> Response: ...
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, object] | None = ...,
        data: object = ...,
        json: object = ...,
        headers: dict[str, str] | None = ...,
        verify: bool = ...,
        timeout: float | int = ...,
        allow_redirects: bool = ...,
    ) -> Response: ...
    def mount(self, prefix: str, adapter: HTTPAdapter) -> None: ...
