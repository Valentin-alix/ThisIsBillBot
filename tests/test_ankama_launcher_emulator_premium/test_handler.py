from unittest import TestCase
from unittest.mock import MagicMock, patch

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.exceptions import HaapiHttpError
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.account_session import AccountGameInfo
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.credentials import (
    DecipheredCertif,
    StoredCertificate,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.server.handler import AnkamaLauncherHandler


class TestAnkamaLauncherHandler(TestCase):
    def test_connect_returns_hash(self) -> None:
        handler = AnkamaLauncherHandler()

        result = handler.connect("dofus", "release", 1, "session-hash")

        self.assertEqual(result, "session-hash")

    def test_settings_get_returns_known_values(self) -> None:
        handler = AnkamaLauncherHandler()

        self.assertEqual(handler.settings_get("session-hash", "autoConnectType"), '"2"')
        self.assertEqual(handler.settings_get("session-hash", "language"), '"fr"')
        self.assertEqual(handler.settings_get("session-hash", "connectionPort"), '"5555"')

    def test_settings_get_rejects_unknown_key(self) -> None:
        handler = AnkamaLauncherHandler()

        with self.assertRaises(NotImplementedError):
            handler.settings_get("session-hash", "unsupported")

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
            "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.server.handler.CryptoHelper.getStoredCertificate",
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
            "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.server.handler.CryptoHelper.getStoredCertificate",
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
            "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.server.handler.CryptoHelper.getStoredCertificate",
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
            "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.server.handler.CryptoHelper.getStoredCertificate",
            side_effect=FileNotFoundError,
        ):
            with self.assertRaises(HaapiHttpError):
                handler.auth_getGameToken("session-hash", 99)

        self.assertIn("session-hash", handler.infos_by_hash)

    def test_auth_get_game_token_with_window_id_ignores_the_window(self) -> None:
        handler = AnkamaLauncherHandler()
        haapi = MagicMock()
        haapi.createToken.return_value = "game-token"
        self._register_session(handler, haapi)

        with patch(
            "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.server.handler.CryptoHelper.getStoredCertificate",
            side_effect=FileNotFoundError,
        ):
            token = handler.auth_getGameTokenWithWindowId("session-hash", 99, 3)

        self.assertEqual(token, "game-token")
        haapi.createToken.assert_called_once_with(99, None)
