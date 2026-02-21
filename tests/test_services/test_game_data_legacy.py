from src.controller.game_data import GameDataFile


def test_legacy_defeat_history_is_not_persisted() -> None:
    game_data = GameDataFile.model_validate({"defeat_count_by_name": {"Monster": 6}})

    assert "defeat_count_by_name" not in game_data.model_dump()
