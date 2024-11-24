import random
from datetime import datetime

from src.utils.metaclasses.singleton import Singleton


class SessionContextService(metaclass=Singleton):
    def __init__(self):
        self.session_start = datetime.now()
        self.energy_level = random.uniform(0.9, 1.1)

    def get_timing_modifier(self) -> float:
        hour = datetime.now().hour
        session_hours = (datetime.now() - self.session_start).total_seconds() / 3600

        time_mod = 1.0
        if 2 <= hour < 8:
            time_mod = random.uniform(1.05, 1.15)
        elif 14 <= hour < 18:
            time_mod = random.uniform(0.92, 0.98)

        fatigue_mod = 1 + min(session_hours * 0.04, 0.15)

        return time_mod * fatigue_mod * self.energy_level

    def refresh_energy(self):
        self.energy_level = random.uniform(0.9, 1.1)
