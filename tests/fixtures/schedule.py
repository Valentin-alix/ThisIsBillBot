from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfile,
    TimeSlot,
)


def make_schedule_profile(
    slots_by_day: dict[str, list[tuple[str, str]]],
    name_fr: str = "Test",
    proxy_id: str = "test-proxy",
) -> ScheduleProfile:
    return ScheduleProfile(
        name_fr=name_fr,
        proxy_id=proxy_id,
        slots_by_day={
            day: [TimeSlot(start=start, end=end) for start, end in slots]
            for day, slots in slots_by_day.items()
        },
    )
