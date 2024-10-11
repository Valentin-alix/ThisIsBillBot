from dataclasses import dataclass, field
from time import sleep

import win32api
import win32con
import win32gui
from pynput.keyboard import Controller as KeyBoardController
from pynput.keyboard import Key as PyKey
from pynput.mouse import Controller as MouseController, Button

from src.windows_manager.window_info import WindowInfo
from src.windows_manager.window_searcher import get_dofus_window_info

type Key = str | int
type Position = tuple[int, int]

EMPTY_POS = (1, 1)


def get_long_param(pos: Position) -> float:
    return win32api.MAKELONG(*pos)


@dataclass
class Controller:
    window_info: WindowInfo
    keyboard: KeyBoardController = field(default_factory=KeyBoardController, init=False)
    mouse: MouseController = field(default_factory=MouseController, init=False)

    def kill_window(self):
        win32gui.PostMessage(self.window_info.hwnd, win32con.WM_CLOSE, 0, 0)

    def set_foreground(self):
        self.keyboard.press(PyKey.alt)
        win32gui.SetForegroundWindow(self.window_info.hwnd)
        self.keyboard.release(PyKey.alt)

    def bg_click(self, pos: Position):
        long_param = get_long_param(pos)
        win32gui.PostMessage(
            self.window_info.hwnd,
            win32con.WM_LBUTTONDOWN,
            win32con.MK_LBUTTON,
            long_param,
        )
        sleep(0.01)
        win32gui.PostMessage(
            self.window_info.hwnd,
            win32con.WM_LBUTTONUP,
            win32con.MK_LBUTTON,
            long_param,
        )

    def click(self, pos: Position):
        self.mouse.position = pos
        sleep(0.05)
        self.mouse.press(Button.left)
        sleep(0.05)
        self.mouse.release(Button.left)

    def void_click(self):
        self.bg_click(EMPTY_POS)


if __name__ == "__main__":
    window = get_dofus_window_info("Vacolat-Angor")
    assert window is not None
    print(window)

    while True:
        controller = Controller(window_info=window)
        controller.void_click()
        sleep(60)
