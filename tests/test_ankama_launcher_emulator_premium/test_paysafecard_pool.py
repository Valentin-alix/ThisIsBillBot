import asyncio
import re
from pathlib import Path
from typing import cast

import pytest
from playwright.async_api import Page

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller import paysafecard_pool
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.paysafecard_pool import (
    PaysafecardPoolController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.subscription.paysafecard_purchase import (
    PaysafecardPaymentOutcome,
    _wait_for_payment_outcome,
)


@pytest.fixture
def paysafecard_pool_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "paysafecards.txt"
    monkeypatch.setattr(paysafecard_pool, "PAYSAFECARDS_PATH", path)
    return path


class _FakeLocator:
    def __init__(self, matches: bool) -> None:
        self._matches = matches

    async def count(self) -> int:
        return int(self._matches)


class _FakePaymentPage:
    def __init__(self, text: str) -> None:
        self._text = text

    def is_closed(self) -> bool:
        return False

    def get_by_text(self, pattern: re.Pattern[str], *, exact: bool) -> _FakeLocator:
        return _FakeLocator(bool(pattern.search(self._text)))

    async def wait_for_timeout(self, timeout: float) -> None:
        raise AssertionError(f"Unexpected payment wait: {timeout}")


def test_selecting_a_pin_does_not_remove_it_from_the_pool(paysafecard_pool_path: Path) -> None:
    paysafecard_pool_path.write_text("first\nsecond\n", encoding="utf-8")
    pool = PaysafecardPoolController()

    assert pool.get_next_pin() == "first"
    assert paysafecard_pool_path.read_text(encoding="utf-8") == "first\nsecond\n"


def test_removing_a_pin_keeps_other_pins(paysafecard_pool_path: Path) -> None:
    paysafecard_pool_path.write_text("first\nsecond\n", encoding="utf-8")

    PaysafecardPoolController().remove_pin("first")

    assert paysafecard_pool_path.read_text(encoding="utf-8") == "second\n"


@pytest.mark.parametrize(
    ("message", "expected_outcome"),
    [
        ("Code invalide", PaysafecardPaymentOutcome.INVALID_PIN),
        ("Solde insuffisant", PaysafecardPaymentOutcome.INSUFFICIENT_BALANCE),
        ("Payment declined", PaysafecardPaymentOutcome.REJECTED),
    ],
)
def test_payment_outcome_distinguishes_removable_cards(
    message: str,
    expected_outcome: PaysafecardPaymentOutcome,
) -> None:
    page = cast(Page, _FakePaymentPage(message))

    outcome = asyncio.run(_wait_for_payment_outcome(page))

    assert outcome is expected_outcome
