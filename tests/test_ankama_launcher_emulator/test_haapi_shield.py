from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
import requests

from ankama_launcher_emulator.exceptions import HaapiHttpError
from ankama_launcher_emulator.haapi.haapi import Haapi
from ankama_launcher_emulator.haapi.urls import ANKAMA_SHIELD_VALIDATE_CODE, ANKAMA_SHIELD_VALIDATE_OTP
from ankama_launcher_emulator.interfaces.credentials import DecipheredCertif


@pytest.fixture
def shield_client(monkeypatch: pytest.MonkeyPatch) -> tuple[Haapi, MagicMock]:
    monkeypatch.setattr(
        "ankama_launcher_emulator.haapi.haapi.CryptoHelper.createHmEncoders",
        lambda: ("hardware-1", "hardware-2"),
    )
    monkeypatch.setattr("ankama_launcher_emulator.haapi.haapi.getpass.getuser", lambda: "test-user")
    client = Haapi(api_key="api-key", login="user@example.com")
    session = MagicMock()
    client.zaap_session = session
    return client, session


@pytest.mark.parametrize(
    ("validate", "endpoint"),
    [(Haapi.validate_code, ANKAMA_SHIELD_VALIDATE_CODE), (Haapi.validate_otp, ANKAMA_SHIELD_VALIDATE_OTP)],
)
def test_shield_validation_sends_device_identity_and_parses_certificate(
    shield_client: tuple[Haapi, MagicMock],
    validate: Callable[[Haapi, str, int], DecipheredCertif],
    endpoint: str,
) -> None:
    client, session = shield_client
    response = MagicMock(spec=requests.Response)
    response.status_code = 200
    response.json.return_value = {"id": 42, "encodedCertificate": "certificate"}
    session.get.return_value = response

    certificate = validate(client, "123456", 102)

    session.get.assert_called_once_with(
        endpoint,
        params={
            "game_id": 102,
            "code": "123456",
            "hm1": "hardware-1",
            "hm2": "hardware-2",
            "name": "launcher-test-user",
        },
        verify=False,
    )
    assert certificate == DecipheredCertif(id=42, encodedCertificate="certificate", login=client.login)


@pytest.mark.parametrize("validate", [Haapi.validate_code, Haapi.validate_otp])
def test_shield_validation_propagates_http_rejection(
    shield_client: tuple[Haapi, MagicMock],
    validate: Callable[[Haapi, str, int], DecipheredCertif],
) -> None:
    client, session = shield_client
    response = MagicMock(spec=requests.Response)
    response.status_code = 403
    response.text = "Invalid security code"
    response.raise_for_status.side_effect = requests.HTTPError("Forbidden")
    session.get.return_value = response

    with pytest.raises(HaapiHttpError, match="Invalid security code") as error:
        validate(client, "123456", 102)

    assert error.value.status_code == 403
