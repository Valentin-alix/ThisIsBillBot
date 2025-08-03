"""Qt callback signatures, type aliases and TypeVars used across the GUI."""

from collections.abc import Callable
from typing import TypeVar

from PyQt6.QtWidgets import QWidget

from ankama_launcher_emulator_premium.interfaces.credentials import StoredApiKey

ProgressCallback = Callable[[str], None]
LaunchGameCallback = Callable[[str, str | None, ProgressCallback | None], int]
StoredAccount = StoredApiKey

BackgroundResultT = TypeVar("BackgroundResultT")
BackgroundTask = Callable[[ProgressCallback], BackgroundResultT]
QtParent = QWidget | None
StoredAccounts = list[StoredApiKey]
