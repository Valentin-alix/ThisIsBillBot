import unittest
from threading import Event
from typing import Callable, TypeVar
from unittest.mock import MagicMock

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey
from google.protobuf.message import Message

from src.core.behaviors.behavior import Behavior
from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals

T = TypeVar("T", bound=Message)

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


class BehaviorTestBase(unittest.TestCase):
    """Base class for testing Behaviors with message injection and interception."""

    def setUp(self):
        self.bot = BotFactory.create_bot(
            SharedSignals(), account=TEST_ACCOUNT, is_fake=True
        )
        self.game_state = self.bot.game_state
        self.event_manager = self.bot.event_manager

        # Track messages sent by behaviors
        self.sent_messages: list[Message] = []
        self._original_send = self.event_manager.send

        # Mock send to intercept outgoing messages
        def mock_send(msg: Message):
            self.sent_messages.append(msg)
            # Optionally call original send if you want real processing
            # self._original_send(msg)

        self.event_manager.send = mock_send

        # Callback tracking
        self.callback_called = Event()
        self.callback_error_code: str | None = None
        self.callback_args = []
        self.callback_kwargs = {}

    def tearDown(self):
        """Cleanup after test."""
        # Restore original send method
        self.event_manager.send = self._original_send

    def inject_server_message(self, msg: Message):
        """Inject a message as if it came from the server."""
        self.event_manager.process_msg(msg)

    def create_callback(self) -> Callable:
        """Create a callback that tracks when it's called."""

        def callback(error_code: str | None = None, *args, **kwargs):
            self.callback_called.set()
            self.callback_error_code = error_code
            self.callback_args = args
            self.callback_kwargs = kwargs

        return callback

    def start_behavior(
        self,
        behavior: Behavior,
        callback: Callable | None = None,
        parent: Behavior | None = None,
        *args,
        **kwargs,
    ):
        """Start a behavior with optional callback tracking."""
        if callback is None:
            callback = self.create_callback()
        behavior.start(callback, parent, *args, **kwargs)

    def wait_for_callback(self, timeout: float = 1.0) -> bool:
        """Wait for the behavior callback to be called."""
        return self.callback_called.wait(timeout)

    def assert_message_sent(self, msg_type: type[Message], count: int = 1):
        """Assert that a specific message type was sent."""
        sent_count = sum(1 for msg in self.sent_messages if isinstance(msg, msg_type))
        assert (
            sent_count == count
        ), f"Expected {count} {msg_type.__name__} messages, got {sent_count}"

    def get_sent_messages(self, msg_type: type[T]) -> list[T]:
        """Get all sent messages of a specific type."""
        return [msg for msg in self.sent_messages if isinstance(msg, msg_type)]

    def get_sent_message(self, msg_type: type[T], index: int = 0) -> T:
        """Get a specific sent message by type and index (default: first message)."""
        messages = self.get_sent_messages(msg_type)
        assert len(messages) > index, f"Expected at least {index + 1} {msg_type.__name__} messages, got {len(messages)}"
        return messages[index]

    def clear_sent_messages(self):
        """Clear the list of sent messages."""
        self.sent_messages.clear()

    def assert_callback_success(self):
        """Assert that the callback was called without error."""
        assert (
            self.callback_called.is_set()
        ), "Callback was not called"
        assert (
            self.callback_error_code is None
        ), f"Callback called with error: {self.callback_error_code}"

    def assert_callback_error(self, expected_error: str):
        """Assert that the callback was called with a specific error code."""
        assert (
            self.callback_called.is_set()
        ), "Callback was not called"
        assert (
            self.callback_error_code == expected_error
        ), f"Expected error '{expected_error}', got '{self.callback_error_code}'"
