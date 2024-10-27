from src.core.behaviors.behavior import Behavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior

BASE_WIDTH: int = 1280
BASE_HEIGHT: int = 720

USABLE_BEHAVIORS: list[type[Behavior]] = [MuleGiveBehavior, MuleAcceptBehavior]
