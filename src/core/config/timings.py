import datetime

TIME_FIGHTER = datetime.timedelta(hours=1, minutes=0)
TIME_HARVESTER = datetime.timedelta(hours=3, minutes=0)

# Waiting times timing
VERY_SMALL_RANGE = (0.2, 0.4)
SMALL_RANGE = (0.3, 1)
BASE_RANGE = (0.5, 1.5)
BIG_RANGE = (1, 3)
ON_NEW_MAP_BEFORE_ACTION = (0.5, 4.5)
# Bank
ON_OPENED_INVENTORY = BASE_RANGE
BEFORE_CLOSING_INVENTORY = BASE_RANGE
# Npc
BETWEEN_REPLY = BASE_RANGE
