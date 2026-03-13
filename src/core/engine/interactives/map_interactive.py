from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import InteractiveElement
from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from DBDofusUnity.dofus_unity_reader.game_constants.skill import SkillEnum

EXIT_SKILL_IDS: frozenset[int] = frozenset({SkillEnum.EXIT, SkillEnum.POINT_OUT_EXIT})


def find_usable_element_ids_by_cell_id(
    map_id: int,
    interactive_element_by_id: dict[int, InteractiveElement],
    skill_id: int | None = None,
) -> dict[int, int]:
    exit_cell_ids = WorldGraphReader().get_exit_cell_ids(map_id)
    ref_by_element_id = MapReader().get_ref_data_by_element_id_by_map_id(map_id)

    element_id_by_cell_id: dict[int, int] = {}
    for element_id, element in interactive_element_by_id.items():
        reference = ref_by_element_id.get(element_id)
        if reference is None or reference.cellId is None or reference.cellId in exit_cell_ids:
            continue
        skill_ids = {enabled_skill.skill_id for enabled_skill in element.enabled_skills}
        if not skill_ids or skill_ids & EXIT_SKILL_IDS:
            continue
        if skill_id is not None and skill_id not in skill_ids:
            continue
        element_id_by_cell_id.setdefault(reference.cellId, element_id)

    return {cell_id: element_id_by_cell_id[cell_id] for cell_id in sorted(element_id_by_cell_id)}
