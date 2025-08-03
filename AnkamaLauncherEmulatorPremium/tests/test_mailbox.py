import imaplib
from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import format_datetime
from io import StringIO
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import patch

from ankama_launcher_emulator_premium.web._client import mailbox as mailbox_module
from ankama_launcher_emulator_premium.web._client.mailbox import (
    ImapMailboxClient,
    MailboxSettings,
)


def _raw_message_with_code(sent_at: datetime, code: str) -> bytes:
    message = EmailMessage()
    message["Date"] = format_datetime(sent_at)
    message["Subject"] = "Code de confirmation Ankama"
    message.set_content(f"Votre code de confirmation est {code}")
    return message.as_bytes()


class _FakeImapClient(imaplib.IMAP4):
    def __init__(self, raw_message: bytes) -> None:
        self.selected_folders: list[tuple[str, bool]] = []
        self.search_calls: list[tuple[str | None, tuple[str, ...]]] = []
        self.fetch_calls: list[tuple[str, str]] = []
        self.store_calls: list[tuple[str, str, str]] = []
        self.expunge_calls = 0
        self.store_status = "OK"
        self.expunge_status = "OK"
        self._raw_message = raw_message

    def select(self, mailbox: str = "INBOX", readonly: bool = False) -> tuple[str, list[bytes | None]]:
        self.selected_folders.append((mailbox, readonly))
        return "OK", []

    def search(self, charset: str | None, *criteria: str) -> tuple[str, list[bytes]]:
        self.search_calls.append((charset, criteria))
        return "OK", [b"1"]

    def fetch(self, message_set: str, message_parts: str) -> tuple[str, list[bytes | tuple[bytes, bytes]]]:
        self.fetch_calls.append((message_set, message_parts))
        return "OK", [(b"1 (BODY[])", self._raw_message)]

    def store(self, message_set: str, command: str, flags: str) -> tuple[str, list[bytes]]:
        self.store_calls.append((message_set, command, flags))
        return self.store_status, []

    def expunge(self) -> tuple[str, list[bytes]]:
        self.expunge_calls += 1
        return self.expunge_status, []


class TestImapMailboxClient(TestCase):
    def test_find_code_deletes_message_after_extracting_code(
        self,
    ) -> None:
        since = datetime(2026, 6, 18, 10, 0, tzinfo=UTC)
        raw_message = _raw_message_with_code(datetime(2026, 6, 18, 10, 1, tzinfo=UTC), "123456")
        imap_client = _FakeImapClient(raw_message)
        mailbox_client = ImapMailboxClient(
            MailboxSettings(host="imap.test", username="user", password="password")
        )

        code = mailbox_client._find_code_in_folder(imap_client, "INBOX", since)

        self.assertEqual(code, "123456")
        self.assertEqual(imap_client.selected_folders, [("INBOX", False)])
        self.assertEqual(
            imap_client.search_calls,
            [(None, ("UNSEEN", "SINCE", "18-Jun-2026"))],
        )
        self.assertEqual(imap_client.fetch_calls, [("1", "(BODY.PEEK[])")])
        self.assertEqual(
            imap_client.store_calls,
            [("1", "+FLAGS", r"(\Deleted)")],
        )
        self.assertEqual(imap_client.expunge_calls, 1)

    def test_find_code_raises_when_message_deletion_fails(self) -> None:
        since = datetime(2026, 6, 18, 10, 0, tzinfo=UTC)
        raw_message = _raw_message_with_code(datetime(2026, 6, 18, 10, 1, tzinfo=UTC), "123456")
        mailbox_client = ImapMailboxClient(
            MailboxSettings(host="imap.test", username="user", password="password")
        )

        expected_errors = {
            "store": "mark mailbox message 1 for deletion",
            "expunge": "expunge mailbox message 1",
        }
        for failed_operation, expected_error in expected_errors.items():
            with self.subTest(failed_operation=failed_operation):
                imap_client = _FakeImapClient(raw_message)
                if failed_operation == "store":
                    imap_client.store_status = "NO"
                else:
                    imap_client.expunge_status = "NO"

                with self.assertRaisesRegex(RuntimeError, expected_error):
                    mailbox_client._find_code_in_folder(imap_client, "INBOX", since)


class _StubManualCodeInput:
    def __init__(self, code: str) -> None:
        self._code = code
        self.drained = False

    def drain(self) -> None:
        self.drained = True

    def poll(self) -> str | None:
        return self._code


class TestManualCodeInput(TestCase):
    def test_read_loop_queues_codes_and_ignores_other_lines(self) -> None:
        manual = mailbox_module.ManualCodeInput()

        with patch.object(mailbox_module.sys, "stdin", StringIO("hello\n\n123456\n")):
            manual._read_loop()

        self.assertEqual(manual.poll(), "123456")
        self.assertIsNone(manual.poll())
        self.assertTrue(manual._closed)

    def test_start_returns_none_when_stdin_is_not_a_terminal(self) -> None:
        with patch.object(mailbox_module.sys, "stdin", StringIO("123456\n")):
            self.assertIsNone(mailbox_module.ManualCodeInput.start())


class TestWaitForCode(IsolatedAsyncioTestCase):
    async def test_wait_for_code_returns_code_typed_in_terminal(self) -> None:
        manual = _StubManualCodeInput("654321")
        mailbox_client = ImapMailboxClient(
            MailboxSettings(host="imap.test", username="user", password="password")
        )

        with (
            patch.object(mailbox_module.ManualCodeInput, "start", return_value=manual),
            patch.object(ImapMailboxClient, "_find_code", return_value=None) as find_code,
        ):
            code = await mailbox_client.wait_for_code(
                since=datetime(2026, 6, 18, 10, 0, tzinfo=UTC), timeout_seconds=5
            )

        self.assertEqual(code, "654321")
        self.assertTrue(manual.drained)
        find_code.assert_called_once()
