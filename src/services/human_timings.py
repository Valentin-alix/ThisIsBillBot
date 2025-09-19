import random
from dataclasses import dataclass

from base_python.singleton import Singleton

from src.core.config import ENABLE_SESSION_CONTEXT
from src.services.session_context import SessionContextService


@dataclass(frozen=True, slots=True)
class TimingProfile:
    minimum_seconds: float
    typical_seconds: float
    maximum_seconds: float

    def __post_init__(self) -> None:
        assert 0 <= self.minimum_seconds <= self.typical_seconds <= self.maximum_seconds, (
            "Timing profile values must satisfy minimum <= typical <= maximum"
        )


REACTION_SHORT_TIMING = TimingProfile(0.2, 0.45, 1.1)
DECISION_NORMAL_TIMING = TimingProfile(0.35, 0.75, 1.8)
MAP_ARRIVAL_TIMING = TimingProfile(0.45, 0.9, 3.9)
HARVEST_REPEAT_TIMING = TimingProfile(0.25, 0.5, 1.2)
BANK_REVIEW_TIMING = TimingProfile(0.5, 1.0, 2.3)
BANK_TRANSFER_TIMING = TimingProfile(0.2, 0.45, 1.0)
BANK_CLOSE_TIMING = TimingProfile(0.4, 0.8, 1.8)
SALE_HOTEL_REVIEW_TIMING = TimingProfile(0.5, 1.0, 2.5)
SALE_HOTEL_PRICE_TIMING = TimingProfile(0.7, 1.3, 3.0)
SALE_HOTEL_SAME_LOT_TIMING = TimingProfile(0.2, 0.3, 0.6)
SALE_HOTEL_NEXT_LOT_TIMING = TimingProfile(0.4, 0.8, 1.2)
SALE_HOTEL_NEXT_ITEM_TIMING = TimingProfile(0.7, 1.4, 2.1)
EQUIPMENT_CHOICE_TIMING = TimingProfile(0.4, 0.9, 2.0)
FIGHT_PLACEMENT_TIMING = TimingProfile(0.35, 0.75, 1.6)
FIGHT_READY_TIMING = TimingProfile(0.45, 0.9, 2.0)
FIGHT_ACTION_TIMING = TimingProfile(0.15, 0.65, 1.8)
FIGHT_SAME_SPELL_ACTION_TIMING = TimingProfile(0.08, 0.3, 0.85)
FIGHT_PASS_TURN_TIMING = TimingProfile(0.25, 0.55, 1.2)
FIGHT_ACKNOWLEDGEMENT_TIMING = TimingProfile(0.01, 0.16, 0.65)
FIGHT_TURN_READY_TIMING = TimingProfile(0.02, 0.35, 1.2)
FIGHT_CHALLENGE_READY_TIMING = TimingProfile(0.3, 0.5, 0.85)
FIGHT_CHALLENGE_SELECTION_TIMING = TimingProfile(0.01, 0.03, 0.08)
FIGHT_POST_COMBAT_TIMING = TimingProfile(0.8, 2.5, 6.0)
FIGHT_SPELL_CAST_TIMING = TimingProfile(0.08, 0.15, 0.3)
ITEM_USE_TIMING = TimingProfile(0.4, 0.6, 1)
WORKSHOP_INTERACTION_TIMING = TimingProfile(0.8, 1.5, 3.0)
LEVEL_UP_CHARACTERISTIC_TIMING = TimingProfile(1, 1.5, 2)
ACHIEVEMENT_REWARD_TIMING = TimingProfile(1.5, 3.0, 6.0)
SHORT_ACTION_TIMING = TimingProfile(0.3, 0.65, 1.0)
BASE_ACTION_TIMING = TimingProfile(0.5, 1.0, 1.5)
LONG_ACTION_TIMING = TimingProfile(1.0, 2.0, 3.0)
VERY_LONG_ACTION_TIMING = TimingProfile(2.0, 4.0, 6.0)
BETWEEN_COLLECT_PAUSE_TIMING = TimingProfile(1.5, 2.75, 4.0)
SESSION_IDLE_DURATION_TIMING = TimingProfile(2.0 * 60, 3.5 * 60, 5.0 * 60)
PLACEMENT_EXTRA_HESITATION_TIMING = TimingProfile(0.25, 0.525, 0.8)


def sample_timing(profile: TimingProfile) -> float:
    wait_time = random.triangular(
        profile.minimum_seconds,
        profile.maximum_seconds,
        profile.typical_seconds,
    )
    if ENABLE_SESSION_CONTEXT:
        wait_time *= SessionContextService().get_timing_modifier()
    return wait_time


def pick_random_weighted_time(mini: float, maxi: float, coeff: float = 5) -> float:
    if mini == 0:
        return 0
    assert coeff >= 1, "Timing coefficient must be at least 1"
    typical = mini + ((maxi - mini) / coeff)
    return random.triangular(mini, maxi, typical)


def get_random_range(range_time: tuple[float, float], is_weighted: bool = True, coeff: float = 5) -> float:
    if is_weighted:
        wait_time = pick_random_weighted_time(*range_time, coeff)
    else:
        wait_time = random.uniform(*range_time)
    if ENABLE_SESSION_CONTEXT:
        wait_time *= SessionContextService().get_timing_modifier()
    return wait_time


class HumanTimingsService(metaclass=Singleton):
    def get_timing_short_action(self) -> float:
        return sample_timing(SHORT_ACTION_TIMING)

    def get_timing_base_action(self) -> float:
        return sample_timing(BASE_ACTION_TIMING)

    def get_timing_long_action(self) -> float:
        return sample_timing(LONG_ACTION_TIMING)

    def get_timing_very_long_action(self) -> float:
        return sample_timing(VERY_LONG_ACTION_TIMING)

    def get_timing_after_map_arrival(self) -> float:
        return sample_timing(MAP_ARRIVAL_TIMING)

    def get_timing_between_collects(self) -> float:
        return sample_timing(BETWEEN_COLLECT_PAUSE_TIMING)

    def get_timing_session_idle_duration(self) -> float:
        return sample_timing(SESSION_IDLE_DURATION_TIMING)

    def get_timing_placement_extra_hesitation(self) -> float:
        return sample_timing(PLACEMENT_EXTRA_HESITATION_TIMING)

    def get_timing_before_spell_cast(self) -> float:
        return sample_timing(FIGHT_SPELL_CAST_TIMING)

    def get_timing_before_item_use(self) -> float:
        return sample_timing(ITEM_USE_TIMING)

    def get_timing_before_workshop_interaction(self) -> float:
        return sample_timing(WORKSHOP_INTERACTION_TIMING)

    def get_timing_before_pass_turn(self) -> float:
        return sample_timing(FIGHT_PASS_TURN_TIMING)

    def get_timing_before_preparation_placement(self) -> float:
        return sample_timing(FIGHT_PLACEMENT_TIMING)

    def get_timing_before_preparation_ready(self) -> float:
        return sample_timing(FIGHT_READY_TIMING)

    def get_timing_free_soul(self) -> float:
        return sample_timing(DECISION_NORMAL_TIMING)

    def get_timing_collect_on_new_map(self) -> float:
        return sample_timing(MAP_ARRIVAL_TIMING)

    def get_timing_attack_on_new_map(self) -> float:
        return sample_timing(MAP_ARRIVAL_TIMING)

    def get_timing_unload_on_bank(self) -> float:
        return sample_timing(BANK_REVIEW_TIMING)

    def get_timing_between_bank_transfers(self) -> float:
        return sample_timing(BANK_TRANSFER_TIMING)

    def get_timing_before_bank_close(self) -> float:
        return sample_timing(BANK_CLOSE_TIMING)

    def get_timing_sale_hotel_review(self) -> float:
        return sample_timing(SALE_HOTEL_REVIEW_TIMING)

    def get_timing_sale_hotel_price_change(self) -> float:
        return sample_timing(SALE_HOTEL_PRICE_TIMING)

    def get_timing_sale_hotel_same_lot(self) -> float:
        return sample_timing(SALE_HOTEL_SAME_LOT_TIMING)

    def get_timing_sale_hotel_next_lot(self) -> float:
        return sample_timing(SALE_HOTEL_NEXT_LOT_TIMING)

    def get_timing_sale_hotel_next_item(self) -> float:
        return sample_timing(SALE_HOTEL_NEXT_ITEM_TIMING)

    def get_timing_equipment_choice(self) -> float:
        return sample_timing(EQUIPMENT_CHOICE_TIMING)

    def get_timing_fight_action(self, same_spell: bool) -> float:
        profile = FIGHT_SAME_SPELL_ACTION_TIMING if same_spell else FIGHT_ACTION_TIMING
        return sample_timing(profile)

    def get_timing_after_level_up(self) -> float:
        return sample_timing(LEVEL_UP_CHARACTERISTIC_TIMING)

    def get_timing_after_achievement(self) -> float:
        return sample_timing(ACHIEVEMENT_REWARD_TIMING)

    def get_timing_fight_acknowledgement(self) -> float:
        return sample_timing(FIGHT_ACKNOWLEDGEMENT_TIMING)

    def get_timing_fight_turn_ready(self) -> float:
        return sample_timing(FIGHT_TURN_READY_TIMING)

    def get_timing_fight_challenge_ready(self) -> float:
        return sample_timing(FIGHT_CHALLENGE_READY_TIMING)

    def get_timing_fight_challenge_selection(self) -> float:
        return sample_timing(FIGHT_CHALLENGE_SELECTION_TIMING)

    def get_timing_after_fight(self) -> float:
        return sample_timing(FIGHT_POST_COMBAT_TIMING)

    def get_timing_npc_dialog_reply(self) -> float:
        base_timing = sample_timing(REACTION_SHORT_TIMING) * random.uniform(0.6, 1.4)
        return base_timing
