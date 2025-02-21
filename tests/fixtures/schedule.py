from src.controller.schedule_profile_controller import (
    ScheduleProfile,
    TimeSlot,
)


def make_schedule_profile(
    slots_by_day: dict[str, list[tuple[str, str]]],
    name_fr: str = "Test",
) -> ScheduleProfile:
    return ScheduleProfile(
        name_fr=name_fr,
        slots_by_day={
            day: [TimeSlot(start=start, end=end) for start, end in slots]
            for day, slots in slots_by_day.items()
        },
    )
