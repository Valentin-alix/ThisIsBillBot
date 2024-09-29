from dataclasses import dataclass, field
from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper

from src.signals.account_signals import AccountSignals
from src.signals.message_signals import MessageInfoSignals
from src.core.logic.inventory import Inventory

from src.interfaces.models.bot import Bot
from src.signals.message_event import MessageEvent
from src.modules.harvester import Harvester
from src.utils import Singleton


@dataclass
class AnkamaLauncher(metaclass=Singleton):
    handler: AnkamaLauncherHandler = field(
        init=False, default_factory=AnkamaLauncherHandler
    )
    account_by_id: dict[int, Bot] = field(default_factory=lambda: {}, init=False)

    def __post_init__(self):
        self.server = AnkamaLauncherServer(self.handler)
        self.account_by_id = self.get_accounts()

    def get_accounts(self) -> dict[int, Bot]:
        account_by_id: dict[int, Bot] = {}
        api_keys_datas = CryptoHelper.getStoredApiKeys()
        for api_key_data in api_keys_datas:
            msg_signals = MessageEvent()
            inventory = Inventory(msg_signals)
            harvester = Harvester(inventory)
            account_by_id[api_key_data["apikey"]["accountId"]] = Bot(
                api_key_data["apikey"]["login"],
                AccountSignals(),
                MessageInfoSignals(),
                msg_signals,
                harvester,
            )
        return account_by_id
