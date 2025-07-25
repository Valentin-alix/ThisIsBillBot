from datetime import datetime

from src.core.bot.kamas_mule_registry import (
    RESERVATION_TTL,
    KamasMuleRegistry,
)


def setup_function() -> None:
    KamasMuleRegistry().clear()


def test_reservation_is_exclusive_and_scoped_to_server() -> None:
    registry = KamasMuleRegistry()
    now = datetime.now()
    registry.mark_ready("mule-a", 1, 100, 200)

    assert registry.reserve(2, 998, now) is None
    reservation = registry.reserve(1, 999, now)

    assert reservation is not None
    assert reservation.mule_character_id == 100
    assert registry.reserve(1, 998, now) is None
    assert registry.is_reserved_by("mule-a", 999)
    assert not registry.is_reserved_by("mule-a", 998)

    registry.release(reservation.token)

    assert registry.reserve(1, 998, now) is not None


def test_first_mule_by_login_is_selected() -> None:
    registry = KamasMuleRegistry()
    now = datetime.now()
    for login, character_id in (
        ("b-mule", 100),
        ("a-mule", 200),
    ):
        registry.mark_ready(login, 1, character_id, 300)

    reservation = registry.reserve(1, 999, now)

    assert reservation is not None
    assert reservation.mule_login == "a-mule"


def test_window_closure_keeps_existing_reservation_until_release() -> None:
    registry = KamasMuleRegistry()
    now = datetime.now()
    registry.mark_ready("mule", 1, 100, 200)
    reservation = registry.reserve(1, 999, now)
    assert reservation is not None

    assert registry.close_window("mule")
    assert registry.is_reserved_by("mule", 999)
    assert registry.reserve(1, 998, now) is None

    registry.release(reservation.token)

    assert not registry.is_reserved_by("mule", 999)
    assert registry.reserve(1, 998, now) is None


def test_expired_reservation_becomes_available_again() -> None:
    registry = KamasMuleRegistry()
    now = datetime.now()
    registry.mark_ready("mule", 1, 100, 200)
    assert registry.reserve(1, 999, now) is not None

    replacement = registry.reserve(1, 998, now + RESERVATION_TTL)

    assert replacement is not None
    assert replacement.donor_character_id == 998
