from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfile,
    TimeSlot,
)
from ankama_launcher_emulator_premium.utils.proxy import ProxyConfig


def make_schedule_profile(
    slots_by_day: dict[str, list[tuple[str, str]]],
    name_fr: str = "Test",
    proxy: ProxyConfig | None = None,
) -> ScheduleProfile:
    resolved_proxy = proxy or ProxyConfig(
        host="127.0.0.1",
        http_port=1081,
        socks_port=1080,
        username="user",
        password="pass",
    )
    return ScheduleProfile(
        name_fr=name_fr,
        proxy=resolved_proxy,
        slots_by_day={
            day: [TimeSlot(start=start, end=end) for start, end in slots]
            for day, slots in slots_by_day.items()
        },
    )
