from dataclasses import dataclass, field

from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.utils import Singleton


@dataclass
class AnkamaLauncher(metaclass=Singleton):
    handler: AnkamaLauncherHandler = field(
        init=False, default_factory=AnkamaLauncherHandler
    )
    account_by_id: dict[int, DecipheredApiKey] = field(
        default_factory=lambda: {}, init=False
    )

    def __post_init__(self):
        self.server = AnkamaLauncherServer(self.handler)
        self.account_by_id = AnkamaLauncher.get_accounts()

    @staticmethod
    def get_accounts() -> dict[int, DecipheredApiKey]:
        account_by_id: dict[int, DecipheredApiKey] = {}
        api_keys_datas = CryptoHelper.getStoredApiKeys()
        for api_key_data in api_keys_datas:
            account_by_id[api_key_data["apikey"]["accountId"]] = api_key_data
        return account_by_id
