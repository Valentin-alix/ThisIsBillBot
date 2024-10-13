from dataclasses import dataclass

from d3_mapping.resources.protos.game.challenge_pb2 import (
    ChallengeModSelectRequest,
)
from d3_mapping.resources.protos.game.common_pb2 import ChallengeMod
from src.const import ON_CHALLENGE
from src.core.behaviors.behavior import Behavior


@dataclass
class FightChallengeBehavior(Behavior):
    def run(self) -> None:
        if self.game_state.player.level < 5:
            return self.finish()

        if self.game_state.fight.challenge_mod == ChallengeMod.CHALLENGE_RANDOM:
            return self.finish()

        request = ChallengeModSelectRequest(challenge_mod=ChallengeMod.CHALLENGE_RANDOM)

        def send_req():
            nonlocal request
            self.event_manager.send(request)
            self.finish()

        self.run_timer(ON_CHALLENGE, send_req)
