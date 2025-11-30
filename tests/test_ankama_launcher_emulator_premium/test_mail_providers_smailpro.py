from datetime import UTC, datetime
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import MagicMock, patch

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.smailpro import (
    RandomMailboxKind,
    SmailProMailProvider,
    SmailProSettings,
    _message_date,
    generate_random_mailbox,
)


def _response(json_body: dict[str, object]) -> MagicMock:
    response = MagicMock()
    response.json.return_value = json_body
    response.raise_for_status.return_value = None
    return response


class TestMessageDate(TestCase):
    def test_parses_gmail_rfc2822_text_date_field(self) -> None:
        message = {"textDate": "Sun, 23 Aug 2026 14:20:44 +0000"}

        self.assertEqual(_message_date(message, "gmail"), datetime(2026, 8, 23, 14, 20, 44, tzinfo=UTC))

    def test_parses_outlook_iso8601_text_date_field(self) -> None:
        message = {"textDate": "2026-08-23T14:26:06Z"}

        self.assertEqual(_message_date(message, "outlook"), datetime(2026, 8, 23, 14, 26, 6, tzinfo=UTC))

    def test_returns_min_when_field_missing(self) -> None:
        self.assertEqual(_message_date({}, "gmail"), datetime.min.replace(tzinfo=UTC))


class TestGenerateRandomMailbox(TestCase):
    def test_calls_dedicated_random_endpoint_for_each_kind(self) -> None:
        cases: list[tuple[RandomMailboxKind, str]] = [
            ("gmail", "/v1/temp_gmail/random"),
            ("outlook", "/v1/temp_outlook/random"),
        ]
        for kind, expected_path in cases:
            with self.subTest(kind=kind):
                response = _response({"email": f"someone+abc@{kind}.com", "timestamp": 1723680000})

                with patch("requests.Session.get", return_value=response) as get:
                    email, timestamp = generate_random_mailbox("api-key", kind)

                self.assertEqual(email, f"someone+abc@{kind}.com")
                self.assertEqual(timestamp, 1723680000)
                get.assert_called_once()
                self.assertTrue(get.call_args.args[0].endswith(expected_path))


class TestSmailProMailProviderWaitForCode(IsolatedAsyncioTestCase):
    async def test_finds_code_from_recent_message(self) -> None:
        inbox_response = _response(
            {
                "messages": [
                    {"mid": "m1", "textDate": "Thu, 18 Jun 2026 10:01:00 +0000"},
                ]
            }
        )
        message_response = _response({"body": "Votre code de confirmation est 123456"})
        provider = SmailProMailProvider(
            SmailProSettings(api_key="api-key", email="temp@gmail.com", kind="gmail", timestamp=1723680000)
        )

        with patch("requests.Session.get", side_effect=[inbox_response, message_response]) as get:
            code = await provider.wait_for_code(
                since=datetime(2026, 6, 18, 10, 0, tzinfo=UTC), timeout_seconds=5
            )

        self.assertEqual(code, "123456")
        inbox_call = get.call_args_list[0]
        self.assertTrue(inbox_call.args[0].endswith("/v1/temp_gmail/inbox"))
        self.assertEqual(inbox_call.kwargs["params"]["timestamp"], 1723680000)

    async def test_ignores_messages_older_than_since(self) -> None:
        inbox_response = _response(
            {
                "messages": [
                    {"mid": "m1", "textDate": "2026-06-18T09:59:00Z"},
                ]
            }
        )
        provider = SmailProMailProvider(
            SmailProSettings(api_key="api-key", email="temp@outlook.com", kind="outlook", timestamp=1716998400)
        )

        with patch("requests.Session.get", side_effect=[inbox_response]) as get:
            code = provider._find_code(since=datetime(2026, 6, 18, 10, 0, tzinfo=UTC))

        self.assertIsNone(code)
        self.assertTrue(get.call_args.args[0].endswith("/v1/temp_outlook/inbox"))
