import psutil
import win32gui
import win32process
from win32process import GetWindowThreadProcessId

from src.windows_manager.window_info import WindowInfo


def get_windows() -> list[WindowInfo]:
    windows: list[WindowInfo] = []

    def win_enum_handler(hwnd: int, _: None):
        window_text = win32gui.GetWindowText(hwnd)
        windows.append(WindowInfo(hwnd=hwnd, name=window_text))

    win32gui.EnumWindows(win_enum_handler, None)

    return windows


def get_window_by_process_and_name(
    target_process_name: str | None = None,
    target_name: str | None = None,
    check_visible: bool = True,
) -> WindowInfo | None:

    for window in get_windows():
        if check_visible and not win32gui.IsWindowVisible(window.hwnd):
            continue
        if target_process_name is not None:
            pid = win32process.GetWindowThreadProcessId(window.hwnd)
            try:
                process_name = psutil.Process(pid[1]).name()
            except psutil.NoSuchProcess:
                continue
            if not process_name == target_process_name:
                continue
        window_text = win32gui.GetWindowText(window.hwnd)
        if target_name and target_name not in window_text:
            continue
        return WindowInfo(hwnd=window.hwnd, name=window_text)

    return None


def get_dofus_window_info(target_name: str) -> WindowInfo | None:
    return get_window_by_process_and_name(
        target_process_name="Dofus.exe", target_name=target_name
    )


def get_process_name_by_window(hwnd: int) -> str:
    _, process_id = GetWindowThreadProcessId(hwnd)
    process = psutil.Process(process_id)
    process_name = process.name()
    return process_name
