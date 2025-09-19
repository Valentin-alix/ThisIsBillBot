from collections import deque

import pytest
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from dofus_unity_reader.game_constants.map_id import MapIdEnum

from src.core.behaviors.quests.quest_script_behavior import get_map_ids_for_coord
from src.core.engine.npcs.dialog_texts import (
    find_npc_reply_ids_matching,
    get_reply_text,
    normalize,
)
from src.core.engine.npcs.npc_lookup import find_monster_ids_by_name, find_npc_ids_by_name
from src.core.engine.quests.quest_criterion import get_required_finished_quest_ids
from dofus_unity_reader.game_constants.world import WorldMapEnum

from src.core.engine.quests.quest_script import (
    FightStep,
    GoToStep,
    QuestScript,
    QuestStep,
    StepWithDestination,
    TalkToNpcStep,
)
from src.core.engine.npcs.reply_selector import ByText
from src.core.engine.quests.scripts import QUEST_SCRIPTS


def _resolve_coord(step: StepWithDestination) -> set[int]:
    assert step.coord is not None
    return get_map_ids_for_coord(step.coord, step.world, step.map_name, step.sub_area_id)


def test_registered_scripts_target_existing_maps() -> None:
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, StepWithDestination) or step.coord is None:
                continue
            map_ids = _resolve_coord(step)
            assert map_ids, f"{script.name} step {index}: no map at {step.coord}"


def test_registered_scripts_map_known_quest_and_step_ids() -> None:
    data_reader = DataReader()
    for script in QUEST_SCRIPTS:
        if script.quest_id is None:
            continue
        assert script.quest_id in data_reader.quest_by_id, (
            f"{script.name}: unknown quest id {script.quest_id}"
        )
        for index, step_id in script.server_step_id_by_index.items():
            assert step_id in data_reader.quest_step_by_id, (
                f"{script.name} step {index}: unknown server step id {step_id}"
            )


def test_step_index_outside_the_script_is_rejected() -> None:
    steps: list[QuestStep] = [GoToStep(map_ids={1})]

    with pytest.raises(ValueError, match="outside of its steps"):
        QuestScript(name="ko", steps=steps, server_step_id_by_index={5: 1})


def test_script_without_step_is_rejected() -> None:
    with pytest.raises(ValueError, match="has no step"):
        QuestScript(name="ko", steps=[])


def test_coord_and_map_ids_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        GoToStep(coord=(3, -17), map_ids={1})


def test_sub_area_id_requires_a_coord() -> None:
    with pytest.raises(ValueError, match="only narrows a coord"):
        GoToStep(map_ids={1}, sub_area_id=95)


def test_go_to_needs_a_destination() -> None:
    with pytest.raises(ValueError, match="needs either coord or map_ids"):
        GoToStep()


def test_talk_to_npc_needs_an_npc_identity() -> None:
    with pytest.raises(ValueError, match="needs either npc_name, npc_id or bones_id"):
        TalkToNpcStep(coord=(3, -17))


def test_map_name_requires_a_coord() -> None:
    with pytest.raises(ValueError, match="only narrows a coord"):
        GoToStep(map_ids={1}, map_name="Banque d'Astrub")


def test_monster_name_and_monster_id_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        FightStep(monster_name="Xelor Louche", monster_id=3363)


def test_world_splits_a_position_that_exists_several_times() -> None:
    """The same position exists on several worlds, and a guide always means the overworld."""
    overworld = get_map_ids_for_coord((3, -17), world=WorldMapEnum.OVERWORLD)
    interiors = get_map_ids_for_coord((3, -17), world=WorldMapEnum.INTERIOR)

    assert overworld
    assert interiors
    assert not overworld & interiors


def test_world_narrows_a_position_to_one_map_on_the_overworld() -> None:
    assert len(get_map_ids_for_coord((7, -19), world=WorldMapEnum.OVERWORLD)) == 1


def test_map_name_narrows_an_ambiguous_interior() -> None:
    all_interiors = get_map_ids_for_coord((6, -18), world=WorldMapEnum.INTERIOR)
    narrowed = get_map_ids_for_coord(
        (6, -18), world=WorldMapEnum.INTERIOR, map_name="Taverne d'Astrub - Chambre du pirate"
    )

    assert len(narrowed) == 1
    assert narrowed < all_interiors


def test_map_name_ignores_accents_and_case() -> None:
    assert get_map_ids_for_coord(
        (6, -18), world=WorldMapEnum.INTERIOR, map_name="TAVERNE D'ASTRUB - CHAMBRE DU PIRATE"
    ) == get_map_ids_for_coord(
        (6, -18), world=WorldMapEnum.INTERIOR, map_name="Taverne d'Astrub - Chambre du pirate"
    )


def test_sub_area_id_narrows_an_ambiguous_coord() -> None:
    all_map_ids = get_map_ids_for_coord((3, -17), world=WorldMapEnum.INTERIOR)
    narrowed = get_map_ids_for_coord((3, -17), world=WorldMapEnum.INTERIOR, sub_area_id=842)

    assert narrowed
    assert narrowed < all_map_ids


def test_registered_scripts_reference_existing_map_ids() -> None:
    data_reader = DataReader()
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, StepWithDestination) or step.map_ids is None:
                continue
            for map_id in step.map_ids:
                assert map_id in data_reader.map_info_by_map_id, (
                    f"{script.name} step {index}: unknown map id {map_id}"
                )


def test_registered_scripts_reference_existing_npcs() -> None:
    data_reader = DataReader()
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, TalkToNpcStep) or step.npc_id is None:
                continue
            assert step.npc_id in data_reader.npc_by_id, (
                f"{script.name} step {index}: unknown npc id {step.npc_id}"
            )


def test_registered_scripts_name_npcs_the_game_knows() -> None:
    """Several npcs may share the name; only a name matching none of them is a typo."""
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, TalkToNpcStep) or step.npc_name is None:
                continue
            assert find_npc_ids_by_name(step.npc_name), (
                f"{script.name} step {index}: no npc is named {step.npc_name!r}"
            )


def test_registered_scripts_name_monsters_the_game_knows() -> None:
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, FightStep) or step.monster_name is None:
                continue
            assert find_monster_ids_by_name(step.monster_name), (
                f"{script.name} step {index}: no monster is named {step.monster_name!r}"
            )


def test_registered_scripts_resolve_every_coord_to_a_single_map() -> None:
    """An ambiguous destination sends the travel behavior to whichever map it feels like."""
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, StepWithDestination) or step.coord is None:
                continue
            map_ids = _resolve_coord(step)
            assert len(map_ids) == 1, (
                f"{script.name} step {index}: {step.coord} on world {step.world} resolves to "
                f"{len(map_ids)} maps, narrow it with map_name or sub_area_id"
            )


def test_registered_scripts_reference_existing_monsters() -> None:
    data_reader = DataReader()
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, FightStep) or step.monster_id is None:
                continue
            assert step.monster_id in data_reader.monsters_by_id, (
                f"{script.name} step {index}: unknown monster id {step.monster_id}"
            )


def test_registered_scripts_have_at_least_one_step() -> None:
    assert QUEST_SCRIPTS, "no quest script registered"


def _step_npc_ids(step: TalkToNpcStep) -> set[int]:
    """Un nom peut designer plusieurs pnj ; ils partagent alors le meme arbre de dialogue."""
    if step.npc_id is not None:
        return {step.npc_id}
    if step.npc_name is not None:
        return find_npc_ids_by_name(step.npc_name)
    return set()


def _by_text_patterns() -> list[tuple[str, int, frozenset[int], str]]:
    """Every `ByText` pattern of every registered script, with the npcs it may be said to."""
    patterns: list[tuple[str, int, frozenset[int], str]] = []
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, TalkToNpcStep):
                continue
            npc_ids = frozenset(_step_npc_ids(step))
            for turn in step.turns:
                if isinstance(turn.reply, ByText):
                    patterns.append((script.name, index, npc_ids, turn.reply.pattern))
    return patterns


def _reply_ids_matching(npc_ids: frozenset[int], pattern: str) -> list[int]:
    return [reply_id for npc_id in sorted(npc_ids) for reply_id in find_npc_reply_ids_matching(npc_id, pattern)]


def test_every_by_text_pattern_matches_a_reply_of_its_npc() -> None:
    """A pattern matching nothing is a typo, and it would silently stall the dialog."""
    for script_name, index, npc_ids, pattern in _by_text_patterns():
        assert _reply_ids_matching(npc_ids, pattern), (
            f"{script_name} step {index}: pattern {pattern!r} matches no reply of npc(s) "
            f"{sorted(npc_ids)}"
        )


def test_every_by_text_pattern_designates_a_single_wording() -> None:
    """Several ids may carry the same wording, but a pattern must not span two wordings.

    Ankama duplicates a reply id par branche de dialogue, et un meme nom peut porter plusieurs
    pnj : matcher plusieurs ids est donc normal.
    Matching two *different* texts is not: the runtime would pick whichever the server offers
    first, which is not a choice the script made.
    """
    for script_name, index, npc_ids, pattern in _by_text_patterns():
        reply_ids = _reply_ids_matching(npc_ids, pattern)
        wordings = {normalize(text) for text in map(get_reply_text, reply_ids) if text is not None}
        assert len(wordings) == 1, (
            f"{script_name} step {index}: pattern {pattern!r} is ambiguous for npc(s) "
            f"{sorted(npc_ids)}, it matches {sorted(wordings)}"
        )


def test_untrusted_objective_maps_really_disagree_with_their_step() -> None:
    """Une exception qui ne sert plus est une garde desarmee pour rien : elle doit sauter."""
    data_reader = DataReader()
    for script in QUEST_SCRIPTS:
        declared = set(script.objective_ids_with_untrusted_map)
        for index, objective_id in script.objective_id_by_index.items():
            if objective_id not in declared:
                continue
            step = script.steps[index]
            if not isinstance(step, StepWithDestination):
                continue
            step_map_ids = set(step.map_ids) if step.map_ids is not None else _resolve_coord(step)
            objective_map_id = data_reader.quest_objective_by_id[objective_id].mapId
            assert objective_map_id not in step_map_ids, (
                f"{script.name} step {index}: objective {objective_id} agrees with the step, "
                f"drop it from objective_ids_with_untrusted_map"
            )
            declared.discard(objective_id)
        assert not declared, (
            f"{script.name}: objective(s) {sorted(declared)} declared as untrusted but never "
            f"mapped to a step with a destination"
        )


def test_registered_scripts_can_reach_their_prerequisites() -> None:
    """A script whose prerequisite has no script of its own can never run on a fresh account."""
    scripted_quest_ids = {script.quest_id for script in QUEST_SCRIPTS}
    for script in QUEST_SCRIPTS:
        if script.quest_id is None:
            continue
        for required_quest_id in get_required_finished_quest_ids(script.quest_id):
            assert required_quest_id in scripted_quest_ids, (
                f"{script.name} requires quest {required_quest_id}, which no script covers"
            )


def _map_ids_reachable_from(start_map_id: int) -> set[int]:
    """Pure world-graph reachability, ignoring criteria -- enough to catch a walled-off map."""
    world_graph = WorldGraphReader()
    queue = deque(world_graph.get_vertexes(start_map_id))
    seen = set(queue)
    reached = {start_map_id}
    while queue:
        vertex = queue.popleft()
        for edge in world_graph.get_outgoing_edges_from_vertex(vertex):
            if edge.m_to in seen:
                continue
            seen.add(edge.m_to)
            reached.add(edge.m_to.m_mapId)
            queue.append(edge.m_to)
    return reached


def test_registered_scripts_target_reachable_maps() -> None:
    """A destination walled off in the world graph fails at run time with `path_not_found`."""
    reachable = _map_ids_reachable_from(MapIdEnum.ASTRUB_STREET_KERUBIM)
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, StepWithDestination):
                continue
            map_ids = set(step.map_ids) if step.map_ids is not None else _resolve_coord(step)
            assert map_ids & reachable, (
                f"{script.name} step {index}: no map of {sorted(map_ids)} is reachable from Astrub"
            )


def test_declared_objectives_match_their_step_destination() -> None:
    """Garde contre le decalage d'index : inserer une etape reassocie tout ce qui suit.

    L'objectif serveur porte la map ou il se valide ; si elle ne correspond pas a la
    destination de l'etape, c'est que le mapping index -> objectif a glisse.
    """
    data_reader = DataReader()
    for script in QUEST_SCRIPTS:
        for index, objective_id in script.objective_id_by_index.items():
            if objective_id in script.objective_ids_with_untrusted_map:
                continue  # map declaree connue fausse, cf. `objective_ids_with_untrusted_map`
            objective_map_id = data_reader.quest_objective_by_id[objective_id].mapId
            if not objective_map_id:
                continue  # certains objectifs ne portent qu'une position, pas de map
            step = script.steps[index]
            if not isinstance(step, StepWithDestination):
                continue
            step_map_ids = set(step.map_ids) if step.map_ids is not None else _resolve_coord(step)
            assert objective_map_id in step_map_ids, (
                f"{script.name} step {index}: objective {objective_id} validates on map "
                f"{objective_map_id}, but the step goes to {sorted(step_map_ids)}"
            )
