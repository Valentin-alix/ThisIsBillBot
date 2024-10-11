from dataclasses import dataclass


@dataclass
class WindowInfo:
    hwnd: int
    name: str

    def __hash__(self) -> int:
        return self.hwnd.__hash__()
