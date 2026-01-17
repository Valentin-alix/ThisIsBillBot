from unittest.mock import Mock, patch

from src.services.league_of_legends import is_league_of_legends_match_running


def test_match_process_is_detected_case_insensitively() -> None:
    process = Mock()
    process.name.return_value = "League of Legends.EXE"

    with patch("src.services.league_of_legends.psutil.process_iter", return_value=[process]):
        assert is_league_of_legends_match_running()


def test_league_client_does_not_block_automation() -> None:
    process = Mock()
    process.name.return_value = "LeagueClient.exe"

    with patch("src.services.league_of_legends.psutil.process_iter", return_value=[process]):
        assert not is_league_of_legends_match_running()
