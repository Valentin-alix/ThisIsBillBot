from PyQt6.QtWidgets import QAbstractScrollArea
from qfluentwidgets.window.stacked_widget import StackedWidget


class NoAnimatedStackedWidget(StackedWidget):
    def setCurrentWidget(self, widget, popOut=True):
        if isinstance(widget, QAbstractScrollArea):
            vsb = widget.verticalScrollBar()
            if vsb is not None:
                vsb.setValue(0)
        self.view.setCurrentWidget(widget, duration=0)
