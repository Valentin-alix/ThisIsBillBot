from collections.abc import Mapping
from http.cookiejar import Cookie, CookieJar
from typing import Any

from .adapters import HTTPAdapter

class HTTPError(Exception): ...
class ConnectionError(Exception): ...
class Timeout(Exception): ...

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
    text: str
    url: str
    status_code: int
    headers: dict[str, str]
    cookies: RequestsCookieJar
    def raise_for_status(self) -> None: ...
    def json(self) -> Any: ...

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
