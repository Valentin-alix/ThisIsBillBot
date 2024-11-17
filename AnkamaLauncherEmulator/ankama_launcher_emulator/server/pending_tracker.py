import logging
import threading
import time
from dataclasses import dataclass, field

from AnkamaLauncherEmulator.ankama_launcher_emulator.redirect import set_proxy
from src.utils.metaclasses.singleton import Singleton

logger = logging.getLogger()

PENDING_TIMEOUT_SECONDS = 60


@dataclass
class PendingConnectionTracker(metaclass=Singleton):
    """
    Thread-safe tracker for pending Dofus connections.
    Manages proxy state based on pending connection count.

    - Enables proxy when first instance launches
    - Disables proxy when last instance's config is intercepted
    - Auto-decrements after timeout if client never connects
    """

    _pending_count: int = field(init=False, default=0)
    _pending_timestamps: list[float] = field(init=False, default_factory=list)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    _cleanup_timer: threading.Timer | None = field(init=False, default=None)

    def register_launch(self):
        with self._lock:
            was_zero = self._pending_count == 0
            self._pending_count += 1
            self._pending_timestamps.append(time.time())

            if was_zero:
                logger.info("[PROXY] Premier lancement, activation proxy")
                set_proxy(True)
            else:
                logger.info(
                    f"[PROXY] Lancement enregistré, {self._pending_count} en attente"
                )

    def register_connection(self):
        with self._lock:
            assert self._pending_count > 0
            self._pending_count -= 1
            self._pending_timestamps.pop(0)
            logger.info(f"[PROXY] Config interceptée, {self._pending_count} en attente")
            if self._pending_count == 0:
                logger.info("[PROXY] Dernier client connecté, désactivation proxy")
                set_proxy(False)

    def _schedule_cleanup(self):
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        self._cleanup_timer = threading.Timer(
            PENDING_TIMEOUT_SECONDS, self._cleanup_expired
        )
        self._cleanup_timer.start()

    def _cleanup_expired(self):
        with self._lock:
            now = time.time()
            expired_count = 0

            while (
                self._pending_timestamps
                and (now - self._pending_timestamps[0]) > PENDING_TIMEOUT_SECONDS
            ):
                self._pending_timestamps.pop(0)
                self._pending_count -= 1
                expired_count += 1

            if expired_count > 0:
                logger.info(
                    f"[PROXY] Timeout: {expired_count} connexion(s) expirée(s), {self._pending_count} en attente"
                )
                if self._pending_count == 0:
                    logger.info("[PROXY] Tous les clients expirés, désactivation proxy")
                    set_proxy(False)
                elif self._pending_timestamps:
                    self._schedule_cleanup()
