from dataclasses import dataclass

from d3_mapping.resources.protos.game.challenge_pb2 import (
    ChallengeModSelectRequest,
)
from d3_mapping.resources.protos.game.common_pb2 import ChallengeMod

from src.core.behaviors.behavior import Behavior
from src.core.config.timings import SMALL_RANGE


@dataclass
class FightChallengeBehavior(Behavior):
    def run(self) -> None:
        if self.game_state.player.level < 5:
            return self.finish()

        if self.game_state.fight.challenge_mod == ChallengeMod.CHALLENGE_RANDOM:
            return self.finish()

        def send_req():
            request = ChallengeModSelectRequest(
                challenge_mod=ChallengeMod.CHALLENGE_RANDOM
            )
            self.event_manager.send(request)
            self.finish()

        self.run_timer(SMALL_RANGE, send_req)
