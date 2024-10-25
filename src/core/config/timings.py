import datetime
from random import uniform


def get_time_beween_sale_hotel_prices():
    return datetime.timedelta(hours=2, minutes=0) * uniform(0.75, 1.25)


def get_time_beween_areas():
    return datetime.timedelta(hours=2, minutes=0) * uniform(0.75, 1.25)


# Waiting times timing
VERY_SMALL_RANGE = (0.2, 0.4)
TINY_RANGE = (0.2, 0.8)
SMALL_RANGE = (0.3, 1)
BASE_RANGE = (0.5, 1.5)
BIG_RANGE = (1, 3)
ON_NEW_MAP_BEFORE_ACTION = (0.5, 4.5)
# Bank
ON_OPENED_INVENTORY = BASE_RANGE
BEFORE_CLOSING_INVENTORY = BASE_RANGE
# Npc
BETWEEN_REPLY = BASE_RANGE


if __name__ == "__main__":
    temp = get_time_beween_areas()
    print(temp)
