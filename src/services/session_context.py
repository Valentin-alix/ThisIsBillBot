import random
from datetime import datetime

from base_python.singleton import Singleton


class SessionContextService(metaclass=Singleton):
    def __init__(self):
        self.session_start = datetime.now()
        self.energy_level = random.uniform(0.95, 1.05)

    def get_timing_modifier(self) -> float:
        hour = datetime.now().hour
        session_hours = (datetime.now() - self.session_start).total_seconds() / 3600

        time_mod = 1.0
        if 2 <= hour < 8:
            time_mod = random.uniform(1.03, 1.08)
        elif 14 <= hour < 18:
            time_mod = random.uniform(0.94, 0.99)

        fatigue_mod = 1 + min(session_hours * 0.025, 0.08)

        return time_mod * fatigue_mod * self.energy_level

    def refresh_energy(self) -> None:
        self.energy_level = random.uniform(0.95, 1.05)
