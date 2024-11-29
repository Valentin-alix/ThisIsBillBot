import unittest

from ankama_launcher_emulator_premium.interfaces.deciphered_api_key import (
    DecipheredApiKey,
)
from google.protobuf.message import Message

from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals

TEST_ACCOUNT: DecipheredApiKey = {
    "apikeyFile": "/path/to/test",
    "apikey": {
        "key": "test_key",
        "provider": "ankama",
        "refreshToken": "test_refresh",
        "isStayLoggedIn": True,
        "accountId": 1,
        "login": "TestBot",
        "certificate": {"id": 1, "encodedCertificate": "test", "login": "TestBot"},
        "refreshDate": 9999999999,
    },
}


class StateTestBase(unittest.TestCase):
    """Base class for testing States via message injection."""

    def setUp(self):
        self.bot = BotFactory.create_bot(
            SharedSignals(), account=TEST_ACCOUNT, is_fake=True
        )
        self.game_state = self.bot.game_state
        self.event_manager = self.bot.event_manager

    def inject(self, msg: Message):
        """Inject a message as if the server sent it."""
        self.event_manager.process_msg(msg)

