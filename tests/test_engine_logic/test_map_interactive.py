from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import InteractiveElement
from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from DBDofusUnity.dofus_unity_reader.game_constants.map_id import MapIdEnum
from DBDofusUnity.dofus_unity_reader.game_constants.skill import SkillEnum

from src.core.engine.interactives.map_interactive import find_usable_element_ids_by_cell_id

POLISH_SKILL_ID = 700


def _element_ids_by_cell_id(map_id: int) -> dict[int, int]:
    references = MapReader().get_ref_data_by_element_id_by_map_id(map_id)
    return {
        reference.cellId: element_id
        for element_id, reference in references.items()
        if reference.cellId is not None
    }


def _elements(element_ids: dict[int, int], skill_id: int = POLISH_SKILL_ID) -> dict[int, InteractiveElement]:
    return {
        element_id: InteractiveElement(
            element_id=element_id,
            on_current_map=True,
            enabled_skills=[InteractiveElement.InteractiveElementSkill(skill_id=skill_id)],
        )
        for element_id in element_ids.values()
    }


def test_exit_cells_are_read_from_the_world_graph() -> None:
    exits = WorldGraphReader().get_exit_cell_ids(MapIdEnum.KERUBIM_SHOP)

    assert exits == {245, 246, 298}


def test_a_map_absent_from_the_graph_has_no_exit_cell() -> None:
    assert WorldGraphReader().get_exit_cell_ids(-1) == frozenset()


def test_the_two_shelves_of_kerubim_upper_floor_are_the_only_non_exit_elements() -> None:
    element_ids = _element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP)

    usable = find_usable_element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP, _elements(element_ids))

    assert list(usable) == [314, 347]


def test_ground_floor_keeps_enough_furniture_for_its_three_objectives() -> None:
    element_ids = _element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP_ENTRANCE)

    usable = find_usable_element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP_ENTRANCE, _elements(element_ids))

    assert len(usable) >= 3
    assert not set(usable) & WorldGraphReader().get_exit_cell_ids(MapIdEnum.KERUBIM_SHOP_ENTRANCE)


def test_an_element_offering_the_exit_skill_is_dropped() -> None:
    element_ids = _element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP)
    elements = _elements(element_ids, skill_id=SkillEnum.EXIT)

    assert find_usable_element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP, elements) == {}


def test_an_element_without_enabled_skill_is_dropped() -> None:
    element_ids = _element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP)
    elements = _elements(element_ids)
    elements[element_ids[314]] = InteractiveElement(element_id=element_ids[314], on_current_map=True)

    usable = find_usable_element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP, elements)

    assert list(usable) == [347]


def test_skill_id_narrows_the_candidates() -> None:
    element_ids = _element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP)
    elements = _elements(element_ids)

    assert find_usable_element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP, elements, POLISH_SKILL_ID)
    assert find_usable_element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP, elements, POLISH_SKILL_ID + 1) == {}


def test_an_element_the_map_does_not_know_is_ignored() -> None:
    elements = {
        999_999: InteractiveElement(
            element_id=999_999,
            on_current_map=True,
            enabled_skills=[InteractiveElement.InteractiveElementSkill(skill_id=POLISH_SKILL_ID)],
        )
    }

    assert find_usable_element_ids_by_cell_id(MapIdEnum.KERUBIM_SHOP, elements) == {}
