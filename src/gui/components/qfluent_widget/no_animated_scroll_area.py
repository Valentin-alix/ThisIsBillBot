from PyQt5.QtWidgets import QScrollArea
from qfluentwidgets.common import SmoothMode
from qfluentwidgets.components.widgets.scroll_bar import SmoothScrollDelegate


class NoAnimatedScrollArea(QScrollArea):
    """Smooth scroll area"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollDelagate = SmoothScrollDelegate(self)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

    def enableTransparentBackground(self):
        self.setStyleSheet("QScrollArea{border: none; background: transparent}")

        if self.widget():
            self.widget().setStyleSheet("QWidget{background: transparent}")
