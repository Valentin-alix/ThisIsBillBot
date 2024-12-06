from PyQt6.QtGui import QIcon

from qfluentwidgets import FluentIcon as FluentIcon, FluentIconBase as FluentIconBase

def toQIcon(icon: str | QIcon | FluentIconBase) -> QIcon: ...
