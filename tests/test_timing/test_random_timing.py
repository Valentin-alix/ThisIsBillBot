from src.common.timing import pick_random_weighted_time
from tests.setup_factory import GameStateFixture


class TestRandomTiming(GameStateFixture):
    def test_weighted_random_timing(self):
        waiting_timings = [pick_random_weighted_time(0.5, 4.5) for i in range(1000)]
        print(sum(waiting_timings) / len(waiting_timings))
