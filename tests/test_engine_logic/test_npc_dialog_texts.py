from src.core.engine.npcs.dialog_texts import (
    find_npc_reply_ids_matching,
    get_question_text,
    get_reply_text,
    matches,
    normalize,
)

KERUBIM_NPC_ID = 1901
KERUBIM_HELP_REPLY_ID = 15482  # "Accepter de l'aider."
KERUBIM_SHOP_CLOSED_MESSAGE_ID = 12877  # "La boutique est fermee pour cause d'inventaire..."
UNKNOWN_ID = 999_999_999


def test_normalize_strips_accents_and_case() -> None:
    assert normalize("Écouter la SUITE.") == "ecouter la suite."


def test_normalize_collapses_whitespace() -> None:
    assert normalize("  Lui   demander\tune plume. ") == "lui demander une plume."


def test_reply_text_comes_from_the_game_data() -> None:
    assert get_reply_text(KERUBIM_HELP_REPLY_ID) == "Accepter de l'aider."


def test_unknown_reply_has_no_text() -> None:
    assert get_reply_text(UNKNOWN_ID) is None


def test_question_text_comes_from_the_game_data() -> None:
    question_text = get_question_text(KERUBIM_SHOP_CLOSED_MESSAGE_ID)

    assert question_text is not None
    assert "boutique est ferm" in question_text


def test_unknown_question_has_no_text() -> None:
    assert get_question_text(UNKNOWN_ID) is None


def test_matching_ignores_accents_and_case() -> None:
    assert matches("ecouter la suite", "Écouter la suite.")
    assert matches("ÉCOUTER LA SUITE", "ecouter la suite.")


def test_matching_is_a_regex_search_not_an_equality() -> None:
    assert matches(r"^lui donner les trois plumes\.$", "Lui donner les trois plumes.")
    assert not matches(r"^donner les trois plumes", "Lui donner les trois plumes.")


def test_unresolved_text_never_matches() -> None:
    assert not matches("anything", None)


def test_finding_replies_of_an_npc_by_wording() -> None:
    assert find_npc_reply_ids_matching(KERUBIM_NPC_ID, r"accepter de l'aider") == [
        KERUBIM_HELP_REPLY_ID
    ]


def test_finding_replies_of_an_unknown_npc_yields_nothing() -> None:
    assert find_npc_reply_ids_matching(UNKNOWN_ID, r"accepter de l'aider") == []
