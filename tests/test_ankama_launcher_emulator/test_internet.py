import socket
from unittest import TestCase
from unittest.mock import MagicMock, patch

import requests
from ankama_launcher_emulator.exceptions import HaapiHttpError
from ankama_launcher_emulator.utils.internet import (
    raise_for_status_with_content,
    retry_internet,
)


class TestRaiseForStatusWithContent(TestCase):
    def test_exposes_the_status_code_and_the_body(self) -> None:
        response = MagicMock()
        response.status_code = 401
        response.text = '{"reason":"EXPIRED"}'
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("401")

        with self.assertRaises(HaapiHttpError) as caught:
            raise_for_status_with_content(response)

        self.assertEqual(caught.exception.status_code, 401)
        self.assertIn("EXPIRED", str(caught.exception))


class TestRetryInternet(TestCase):
    def test_retry_internet_retries_then_returns_value(self) -> None:
        attempts = {"count": 0}

        @retry_internet
        def flaky_call() -> str:
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise requests.exceptions.ConnectionError("offline")
            return "ok"

        with patch("ankama_launcher_emulator.utils.internet.sleep") as sleep_mock:
            result = flaky_call()

        self.assertEqual(result, "ok")
        self.assertEqual(attempts["count"], 2)
        sleep_mock.assert_called_once_with(10)

    def test_retry_internet_raises_after_exhausting_retries(self) -> None:
        attempts = 0

        @retry_internet
        def always_fails() -> str:
            nonlocal attempts
            attempts += 1
            raise socket.gaierror("dns")

        with (
            patch("ankama_launcher_emulator.utils.internet.sleep") as sleep_mock,
            self.assertRaises(requests.exceptions.ConnectionError),
        ):
            always_fails()

        self.assertEqual(attempts, 3)
        self.assertEqual(sleep_mock.call_count, 2)
