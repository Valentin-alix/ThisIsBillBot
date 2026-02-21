from unittest.mock import patch

from src.services.human_timings import HumanTimingsService


def test_samples_the_timing_profile() -> None:
    with (
        patch("src.services.human_timings.random.triangular", return_value=2.0),
        patch("src.services.human_timings.ENABLE_SESSION_CONTEXT", False),
    ):
        timing = HumanTimingsService().get_timing_before_spell_cast()

    assert timing == 2.0
