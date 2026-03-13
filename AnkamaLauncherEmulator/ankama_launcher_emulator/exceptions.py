import requests
class BannedException(Exception): ...


class ProxyRejectedError(Exception):
    pass


class HaapiHttpError(requests.exceptions.HTTPError):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code
