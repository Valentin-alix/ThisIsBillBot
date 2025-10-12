from functools import lru_cache

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader

from src.core.engine.npcs.dialog_texts import normalize


@lru_cache(maxsize=1)
def _npc_ids_by_normalized_name() -> dict[str, list[int]]:
    npc_ids_by_name: dict[str, list[int]] = {}
    for name, npc_ids in DataReader().npc_ids_by_name.items():
        npc_ids_by_name.setdefault(normalize(name), []).extend(npc_ids)
    return npc_ids_by_name


def find_npc_ids_by_name(name: str) -> set[int]:
    return set(_npc_ids_by_normalized_name().get(normalize(name), []))


@lru_cache(maxsize=1)
def _monster_ids_by_normalized_name() -> dict[str, list[int]]:
    monster_ids_by_name: dict[str, list[int]] = {}
    for name, monster_ids in DataReader().monster_ids_by_name.items():
        monster_ids_by_name.setdefault(normalize(name), []).extend(monster_ids)
    return monster_ids_by_name


def find_monster_ids_by_name(name: str) -> set[int]:
    return set(_monster_ids_by_normalized_name().get(normalize(name), []))
