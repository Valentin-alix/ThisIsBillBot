import datetime
from google.protobuf.message import Message

TIME_BETWEEN_SALE_HOTEL = datetime.timedelta(hours=2, minutes=0)

# Waiting times timing
VERY_SMALL_RANGE = (0.2, 0.4)
SMALL_RANGE = (0.3, 1)
BASE_RANGE = (0.5, 1.5)
ON_NEW_MAP_BEFORE_ACTION = (0.5, 4.5)
# Bank
ON_OPENED_INVENTORY = BASE_RANGE
BEFORE_CLOSING_INVENTORY = BASE_RANGE
# Fight
ON_STARTED_FIGHT = BASE_RANGE
ON_PLAYER_TURN = SMALL_RANGE
ON_PLAYER_MOVED = SMALL_RANGE
ON_PLAYED_SPELL = VERY_SMALL_RANGE
ON_CHALLENGE = VERY_SMALL_RANGE
# Npc
BETWEEN_REPLY = BASE_RANGE


def get_human_timing_between_messages(first_msg: Message, second_msg: Message): ...
