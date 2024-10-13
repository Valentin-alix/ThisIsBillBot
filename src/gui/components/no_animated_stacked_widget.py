from PyQt5.QtWidgets import QAbstractScrollArea
from qfluentwidgets.window.stacked_widget import StackedWidget


class NoAnimatedStackedWidget(StackedWidget):
    def setCurrentWidget(self, widget, popOut=True):
        if isinstance(widget, QAbstractScrollArea):
            widget.verticalScrollBar().setValue(0)
        self.view.setCurrentWidget(widget, duration=0)
