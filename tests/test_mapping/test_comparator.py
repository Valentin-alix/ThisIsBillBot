import unittest

from D3Mapping.d3_mapping.consts import (
    OBFUSCATED_PROTO_CONNECTION,
    OBFUSCATED_PROTO_GAME,
    PROTO_CONNECTION_PATH,
    PROTO_GAME_PATH,
)
from D3Mapping.d3_mapping.factories.p_mapper_factory import PMapperFactory
from D3Mapping.tests.utils import ComparisonInfo, test_comparisons


class TestComparator(unittest.TestCase):
    def setUp(self) -> None:
        self.game_p_mapper = PMapperFactory.create_p_mapper(
            PROTO_GAME_PATH, OBFUSCATED_PROTO_GAME
        )
        self.conn_p_mapper = PMapperFactory.create_p_mapper(
            PROTO_CONNECTION_PATH, OBFUSCATED_PROTO_CONNECTION
        )
        return super().setUp()

    def test_conn_msgs(self):
        comparisons: list[ComparisonInfo] = [
            (
                ".com.ankama.dofus.server.connection.protocol.LoginMessage",
                "kbv",
                None,
                None,
            )
        ]
        test_comparisons(self.conn_p_mapper, comparisons)

    def test_game_msgs(self):
        comparisons: list[ComparisonInfo] = [
            (
                ".com.ankama.dofus.server.game.protocol.game.action.GameActionFightCastRequest",
                "iho",
                None,
                None,
            ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.fight.preparation.FightJoinRequest",
            #     "ilt",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.context.EntitiesDispositionEvent",
            #     "iua",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.fight.preparation.FightPlacementPositionRequest",
            #     "ilt",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.StatedElement",
            #     "jex",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.ActorPositionInformation.ActorInformation.RolePlayActor",
            #     "jhp.jhn.jgx",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.interactive.element.InteractiveUseRequest",
            #     "hza",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.Request",
            #     "hcm",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.ActorPositionInformation.ActorInformation.FightFighterInformation",
            #     "jhp.jhn.jgx",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.MonsterGroupStaticInformation",
            #     "jlx",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.gamemap.MapMovementRequest",
            #     "ifq",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.gamemap.MapMovementConfirmResponse",
            #     "ifs",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.MapExtendedCoordinates",
            #     "igp",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.House",
            #     "jfl",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.gamemap.MapComplementaryInformationEvent",
            #     "ifo",
            #     None,
            #     None,
            # ),
            # message ActorInformation {
            #     .com.ankama.dofus.server.game.protocol.common.EntityLook look = 1;
            #     oneof information {
            #         .com.ankama.dofus.server.game.protocol.common.ActorPositionInformation.ActorInformation.RolePlayActor role_play_actor = 2;
            #         .com.ankama.dofus.server.game.protocol.common.ActorPositionInformation.ActorInformation.FightFighterInformation fighter = 3;
            # }
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.ActorPositionInformation.ActorInformation",
            #     "jhp.jhn",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.common.ActorPositionInformation",
            #     "jmw",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.guild.application.GuildApplicationListenRequest",
            #     "ifo",
            #     None,
            #     None,
            # ),
            # (
            #     ".com.ankama.dofus.server.game.protocol.achievement.Achievement",
            #     "hco",
            #     None,
            #     None,
            # ),
        ]
        test_comparisons(self.game_p_mapper, comparisons)
