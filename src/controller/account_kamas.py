import os
from threading import RLock

from pydantic import RootModel
from python_utils.singleton import Singleton

from src.const import RESOURCE_FOLDER


class AccountKamasByLogin(RootModel[dict[str, int]]):
    """Persisted last-known kamas amount keyed by account login."""


class AccountKamasController(metaclass=Singleton):
    _LOCK = RLock()
    _FILE_PATH = os.path.join(RESOURCE_FOLDER, "account_kamas.local.json")

    def get_kamas(self, login: str) -> int | None:
        with self._LOCK:
            return self._read_kamas_by_login().get(login)

    def record_kamas(self, login: str, kamas: int) -> None:
        assert kamas >= 0, f"Kamas cannot be negative: {kamas}"
        with self._LOCK:
            kamas_by_login = self._read_kamas_by_login()
            kamas_by_login[login] = kamas
            self._write_kamas_by_login(kamas_by_login)

    def _read_kamas_by_login(self) -> dict[str, int]:
        if not os.path.exists(self._FILE_PATH):
            return {}
        with open(self._FILE_PATH, encoding="utf-8") as handle:
            return AccountKamasByLogin.model_validate_json(handle.read()).root

    def _write_kamas_by_login(self, kamas_by_login: dict[str, int]) -> None:
        os.makedirs(os.path.dirname(self._FILE_PATH), exist_ok=True)
        with open(self._FILE_PATH, "w", encoding="utf-8") as handle:
            handle.write(AccountKamasByLogin(kamas_by_login).model_dump_json(indent=2))
