import unittest
from datetime import datetime

from dateutil import relativedelta

from src.core.bot.lifecycle.scheduler import is_in_playtime


class TestPlaytime(unittest.TestCase):
    def test_is_bot_in_playtime(self):
        now = datetime.now()

        infos = [
            ((4, 00), ["03:00"], ["12:00"], True),
            ((4, 00), ["22:00"], ["08:00"], True),
            ((4, 00), ["22:00"], ["03:00"], False),
        ]

        for (hour, min), playtime_starts, playtime_ends, in_range in infos:
            assert (
                is_in_playtime(
                    datetime(
                        year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=hour,
                        minute=min,
                    ),
                    playtime_starts,
                    playtime_ends,
                )
                is in_range
            )

    def test_is_bot_not_in_playtime(self):
        now = datetime.now() - relativedelta.relativedelta(days=2)

        infos = [
            ((4, 00), ["03:00"], ["12:00"], False),
        ]

        for (hour, min), playtime_starts, playtime_ends, in_range in infos:
            assert (
                is_in_playtime(
                    datetime(
                        year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=hour,
                        minute=min,
                    ),
                    playtime_starts,
                    playtime_ends,
                )
                is in_range
            )
