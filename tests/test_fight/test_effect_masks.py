import unittest

from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    SpawnInformation,
    Team,
)

from src.core.engine.fights.effect import is_included_by_mask


def _make_actor(actor_id: int, team: Team) -> ActorPositionInformation:
    return ActorPositionInformation(
        actor_id=actor_id,
        actor_information=ActorPositionInformation.ActorInformation(
            fighter=ActorPositionInformation.ActorInformation.FightFighterInformation(
                spawn_information=SpawnInformation(team=team)
            )
        ),
    )


class TestEffectMasks(unittest.TestCase):
    def test_self_target_masks_are_included(self) -> None:
        caster = _make_actor(1, Team.TEAM_CHALLENGER)

        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["c"], caster))
        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["C"], caster))
        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["a"], caster))

    def test_same_team_masks_are_included(self) -> None:
        ally = _make_actor(2, Team.TEAM_CHALLENGER)

        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["d"], ally))
        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["g"], ally))
        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["a"], ally))

    def test_enemy_masks_are_included(self) -> None:
        enemy = _make_actor(2, Team.TEAM_DEFENDER)

        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["A"], enemy))
        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["D"], enemy))

    def test_unknown_masks_return_false(self) -> None:
        enemy = _make_actor(2, Team.TEAM_DEFENDER)

        self.assertFalse(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["?"], enemy))

    def test_any_matching_mask_is_enough(self) -> None:
        enemy = _make_actor(2, Team.TEAM_DEFENDER)

        self.assertTrue(is_included_by_mask(1, Team.TEAM_CHALLENGER, ["?", "A"], enemy))
