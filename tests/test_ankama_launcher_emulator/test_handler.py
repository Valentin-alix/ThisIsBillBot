from unittest import TestCase
from unittest.mock import MagicMock, patch

from ankama_launcher_emulator.exceptions import HaapiHttpError
from ankama_launcher_emulator.interfaces.account_session import AccountGameInfo
from ankama_launcher_emulator.interfaces.credentials import (
    DecipheredCertif,
    StoredCertificate,
)
from ankama_launcher_emulator.server.handler import AnkamaLauncherHandler


class TestAnkamaLauncherHandler(TestCase):
    @staticmethod
    def _register_session(handler: AnkamaLauncherHandler, haapi: MagicMock) -> None:
        handler.infos_by_hash["session-hash"] = AccountGameInfo(
            login="user@example.com",
            game_id=102,
            api_key="api-key",
            haapi=haapi,
        )

    def test_auth_get_game_token_uses_the_stored_certificate(self) -> None:
        handler = AnkamaLauncherHandler()
        certificate = DecipheredCertif(
            id=123,
            encodedCertificate="encoded-certificate",
            login="user@example.com",
        )
        haapi = MagicMock()
        haapi.createToken.return_value = "game-token"
        self._register_session(handler, haapi)

        with patch(
            "ankama_launcher_emulator.server.handler.CryptoHelper.getStoredCertificate",
            return_value=StoredCertificate(certificate=certificate),
        ):
            token = handler.auth_getGameToken("session-hash", 99)

        self.assertEqual(token, "game-token")
        haapi.createToken.assert_called_once_with(99, certificate)

    def test_auth_get_game_token_drops_the_certificate_when_it_is_missing(self) -> None:
        handler = AnkamaLauncherHandler()
        haapi = MagicMock()
        haapi.createToken.return_value = "game-token"
        self._register_session(handler, haapi)

        with patch(
            "ankama_launcher_emulator.server.handler.CryptoHelper.getStoredCertificate",
            side_effect=FileNotFoundError,
        ):
            token = handler.auth_getGameToken("session-hash", 99)

        self.assertEqual(token, "game-token")
        haapi.createToken.assert_called_once_with(99, None)

    def test_auth_get_game_token_drops_the_session_when_haapi_rejects_it(self) -> None:
        handler = AnkamaLauncherHandler()
        haapi = MagicMock()
        haapi.createToken.side_effect = HaapiHttpError("expired", 401)
        self._register_session(handler, haapi)

        with patch(
            "ankama_launcher_emulator.server.handler.CryptoHelper.getStoredCertificate",
            side_effect=FileNotFoundError,
        ):
            with self.assertRaises(HaapiHttpError):
                handler.auth_getGameToken("session-hash", 99)

        self.assertNotIn("session-hash", handler.infos_by_hash)

    def test_auth_get_game_token_keeps_the_session_on_other_errors(self) -> None:
        handler = AnkamaLauncherHandler()
        haapi = MagicMock()
        haapi.createToken.side_effect = HaapiHttpError("boom", 500)
        self._register_session(handler, haapi)

        with patch(
            "ankama_launcher_emulator.server.handler.CryptoHelper.getStoredCertificate",
            side_effect=FileNotFoundError,
        ):
            with self.assertRaises(HaapiHttpError):
                handler.auth_getGameToken("session-hash", 99)

        self.assertIn("session-hash", handler.infos_by_hash)
