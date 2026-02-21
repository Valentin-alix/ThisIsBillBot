import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum, auto


class SessionActivity(StrEnum):
    IDLE = auto()
    QUEST = auto()
    DUNGEON = auto()
    CRAFT = auto()
    SALE_HOTEL = auto()


@dataclass(frozen=True)
class SessionActivitySlot:
    activity: SessionActivity
    starts_at: datetime


@dataclass
class SessionActivityPlan:
    session_start: datetime
    session_end: datetime
    slots: list[SessionActivitySlot]
    completed_activities: set[SessionActivity] = field(default_factory=set[SessionActivity])

    @classmethod
    def create(
        cls,
        session_start: datetime,
        session_end: datetime,
        activities: list[SessionActivity],
    ) -> "SessionActivityPlan":
        assert session_end > session_start, "A session activity plan requires a positive duration"

        duration = session_end - session_start
        starts_at_by_index = [
            session_start + (duration * _get_activity_start_fraction(activity_index, len(activities)))
            for activity_index in range(len(activities))
        ]

        shuffled_activities = list(activities)
        random.shuffle(shuffled_activities)
        slots = [
            SessionActivitySlot(activity=activity, starts_at=starts_at_by_index[activity_index])
            for activity_index, activity in enumerate(shuffled_activities)
        ]
        return cls(session_start=session_start, session_end=session_end, slots=slots)

    def get_due_activity(self, now: datetime) -> SessionActivity | None:
        for slot in self.slots:
            if slot.activity not in self.completed_activities and now >= slot.starts_at:
                return slot.activity
        return None

    def mark_activity_completed(self, activity: SessionActivity) -> None:
        self.completed_activities.add(activity)

    def discard_empty_activity(self, activity: SessionActivity, now: datetime) -> None:
        self.completed_activities.add(activity)
        remaining_activities = [
            slot.activity for slot in self.slots if slot.activity not in self.completed_activities
        ]
        if now >= self.session_end or not remaining_activities:
            self.slots = []
            return

        duration = self.session_end - now
        self.slots = [
            SessionActivitySlot(
                activity=remaining_activity,
                starts_at=now
                + (duration * _get_activity_start_fraction(activity_index, len(remaining_activities))),
            )
            for activity_index, remaining_activity in enumerate(remaining_activities)
        ]


def _get_activity_start_fraction(activity_index: int, activity_count: int) -> float:
    assert activity_count > 0, "An activity start fraction requires at least one activity"
    assert 0 <= activity_index < activity_count, "Activity index must belong to the session plan"
    segment_size = 1 / (activity_count + 1)
    minimum_fraction = (activity_index + 0.75) * segment_size
    maximum_fraction = (activity_index + 1.25) * segment_size
    return random.uniform(minimum_fraction, maximum_fraction)
