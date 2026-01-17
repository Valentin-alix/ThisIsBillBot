import psutil


_MATCH_PROCESS_NAME = "league of legends.exe"


def is_league_of_legends_match_running() -> bool:
    for process in psutil.process_iter():
        try:
            if process.name().casefold() == _MATCH_PROCESS_NAME:
                return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False
