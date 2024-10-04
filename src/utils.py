import random
from time import sleep

import numpy as np

from src.consts import RANGE_WAIT


def pick_random_weighted_time(mini: float, maxi: float, coeff: float = 2) -> float:
    if mini == 0:
        return 0

    steps: list[float] = [round(time, 3) for time in np.arange(mini, maxi, 0.05)]
    wait_time = random.choices(steps, [1 / (step**coeff) for step in steps], k=1)[0]
    return random.uniform(wait_time, wait_time * 1.05)


def wait(
    range_time: tuple[float, float] = RANGE_WAIT,
    is_weighted: bool = True,
    coeff: int = 2,
):
    if is_weighted:
        wait_time = pick_random_weighted_time(*range_time, coeff)
    else:
        wait_time = random.uniform(*range_time)

    sleep(wait_time)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
