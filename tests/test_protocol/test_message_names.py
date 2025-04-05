import datas.protos.non_obf.game.alliance_conquest_pb2 as alliance_conquest_pb2

from src.protocol.message_names import (
    build_non_obf_game_message_pinned_name,
    find_non_obf_game_message_descriptor,
    load_non_obf_game_message_full_names,
)


class TestMessageNames:
    def test_loads_full_non_obf_message_names_for_pinning(self) -> None:
        full_names = load_non_obf_game_message_full_names()

        assert (
            "Com.Ankama.Dofus.Server.Game.Protocol.Alliance.Conquest.AVAStateUpdateRequest"
            in full_names
        )

    def test_find_descriptor_accepts_full_pinned_name(self) -> None:
        descriptor = find_non_obf_game_message_descriptor(
            "Com.Ankama.Dofus.Server.Game.Protocol.Alliance.Conquest.AVAStateUpdateRequest"
        )

        assert descriptor is alliance_conquest_pb2.AVAStateUpdateRequest.DESCRIPTOR

    def test_find_descriptor_keeps_top_level_short_name_lookup(self) -> None:
        descriptor = find_non_obf_game_message_descriptor("AVAStateUpdateRequest")

        assert descriptor is alliance_conquest_pb2.AVAStateUpdateRequest.DESCRIPTOR

    def test_builds_full_name_for_nested_descriptor(self) -> None:
        descriptor = find_non_obf_game_message_descriptor(
            "com.ankama.dofus.server.game.protocol.game.action.GameActionFightEvent.CarryCharacter"
        )
        assert descriptor is not None

        assert (
            build_non_obf_game_message_pinned_name(descriptor)
            == "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionFightEvent.CarryCharacter"
        )
