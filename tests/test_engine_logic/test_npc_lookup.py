from src.core.engine.npcs.npc_lookup import find_monster_ids_by_name, find_npc_ids_by_name

KERUBIM_CREPIN_NPC_ID = 1901
XELOR_LOUCHE_MONSTER_ID = 3363


def test_a_shared_name_yields_every_candidate() -> None:
    npc_ids = find_npc_ids_by_name("Kerubim Crepin")

    assert KERUBIM_CREPIN_NPC_ID in npc_ids
    assert len(npc_ids) > 1


def test_npc_names_ignore_accents_and_case() -> None:
    assert find_npc_ids_by_name("kerubim crépin") == find_npc_ids_by_name("KERUBIM CREPIN")


def test_monster_names_ignore_accents_and_case() -> None:
    assert find_monster_ids_by_name("xélor louche") == {XELOR_LOUCHE_MONSTER_ID}
