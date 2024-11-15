import os
import time
import unittest

from src.const import RECORDING_FOLDER
from src.tools.recorder import Recorder
from tests.fixtures.dummy_models import DummyBot
from tests.fixtures.random_generator import generate_random_bot
from tests.fixtures.random_proto_generators import generate_ExchangeCraftCountRequest


class TestRecorder(unittest.TestCase):
    def test_record_and_replay_message_and_state(self):
        rec = Recorder(max_in_memory=100)
        path = rec.start_session("testsession")

        msg = generate_ExchangeCraftCountRequest()
        payload = msg.SerializeToString()
        rec.record_message("bot1", payload, msg.DESCRIPTOR.full_name, from_server=True)
        rec.snapshot_state("bot1", {"player": {"foo": 42, "bar": "hello"}})

        saved = rec.stop_session()
        assert saved is not None and os.path.exists(saved)

        bot = DummyBot()
        rec.replay(bot, saved, preserve_timing=False, dry_run=False)  # type: ignore

        timeout = time.time() + 5
        while time.time() < timeout:
            if len(bot.event_manager.received) >= 1 and bot.game_state.player.foo == 42:
                break
            time.sleep(0.05)

        assert bot.game_state.player.foo == 42
        assert len(bot.event_manager.received) >= 1

    def test_replay_snapshot(self):
        bot = generate_random_bot()
        bot.replay(os.path.join(RECORDING_FOLDER, "collect_&_fight.jsonl"))

        print(bot.game_state.fight.count_casted_by_spell_id)

        for thread, worker in bot._thread_worker_runnings:
            thread.wait()
