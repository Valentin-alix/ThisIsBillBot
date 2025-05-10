from DBDofusUnity.datas.protos.obf.game import game_messages_pb2
from datas.protos.non_obf.game.game_action_pb2 import EntitySpawnInformation
from src.protocol.protocol_game import get_clear_msg_from_obf


def test_entity_spawn_monster_mapping_survives_obfuscated_transform() -> None:
    obfuscated_spawn = game_messages_pb2.iyc()
    obfuscated_spawn.ParseFromString(bytes.fromhex("120508f0281001"))

    clear_spawn = get_clear_msg_from_obf(obfuscated_spawn)

    assert isinstance(clear_spawn, EntitySpawnInformation)
    assert clear_spawn.HasField("monster")
    assert clear_spawn.monster.monster_gid == 5232
    assert clear_spawn.monster.grade == 1
