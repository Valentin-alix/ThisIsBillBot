from datetime import datetime
import random

import numpy as np


def is_in_playtime(
    now: datetime, playtime_starts: list[str], playtime_ends: list[str]
) -> bool:
    current_time = now

    current_date = datetime.now()

    for start_str, end_str in zip(playtime_starts, playtime_ends):
        start_hour, start_min = start_str.split(":")
        start = datetime(
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            hour=int(start_hour),
            minute=int(start_min),
        )
        end_hour, end_min = end_str.split(":")
        end = datetime(
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            hour=int(end_hour),
            minute=int(end_min),
        )

        if start <= end:
            if start <= current_time <= end:
                return True
        else:
            if current_time >= start or current_time <= end:
                return True

    return False


def pick_random_weighted_time(mini: float, maxi: float, coeff: float = 5) -> float:
    if mini == 0:
        return 0

    steps: list[float] = [round(time, 3) for time in np.arange(mini, maxi, 0.05)]  # type: ignore
    wait_time = random.choices(steps, [1 / (step**coeff) for step in steps])[0]
    return random.uniform(wait_time, wait_time * 1.05)


def get_random_range(
    range_time: tuple[float, float], is_weighted: bool = True, coeff: float = 5
):
    if is_weighted:
        wait_time = pick_random_weighted_time(*range_time, coeff)
    else:
        wait_time = random.uniform(*range_time)

    return wait_time
