import random

import numpy as np


def pick_random_weighted_time(mini: float, maxi: float, coeff: float = 3) -> float:
    if mini == 0:
        return 0

    steps: list[float] = [round(time, 3) for time in np.arange(mini, maxi, 0.05)]
    wait_time = random.choices(steps, [1 / (step**coeff) for step in steps])[0]
    return random.uniform(wait_time, wait_time * 1.05)


def get_random_range(
    range_time: tuple[float, float],
    is_weighted: bool = True,
    coeff: int = 2,
):
    if is_weighted:
        wait_time = pick_random_weighted_time(*range_time, coeff)
    else:
        wait_time = random.uniform(*range_time)

    return wait_time


if __name__ == "__main__":
    temps = [pick_random_weighted_time(0.5, 4.5) for i in range(1000)]
    print(sum(temps) / len(temps))
