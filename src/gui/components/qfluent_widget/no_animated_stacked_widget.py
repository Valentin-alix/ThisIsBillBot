from PyQt6.QtWidgets import QAbstractScrollArea, QWidget
from qfluentwidgets.window.stacked_widget import StackedWidget


class NoAnimatedStackedWidget(StackedWidget):
    def setCurrentWidget(self, widget: QWidget, popOut: bool = True) -> None:
        del popOut
        if isinstance(widget, QAbstractScrollArea):
            vsb = widget.verticalScrollBar()
            if vsb is not None:
                vsb.setValue(0)
        self.view.setCurrentWidget(widget, duration=0)
