from PyQt6.QtWidgets import QWidget
from qfluentwidgets.components.widgets.flyout import (
    Flyout,
    FlyoutViewBase,
)

class AcrylicFlyoutViewBase(FlyoutViewBase): ...

class AcrylicFlyout(Flyout):
    def __init__(self, view: FlyoutViewBase, parent: QWidget | None = None) -> None: ...
