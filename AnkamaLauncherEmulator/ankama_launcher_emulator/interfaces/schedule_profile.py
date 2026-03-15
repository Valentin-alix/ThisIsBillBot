from pydantic import BaseModel, Field

SCHEDULE_RANDOM_MINUTES_MIN = 10
SCHEDULE_RANDOM_MINUTES_MAX = 30


class ProxyConfig(BaseModel):
    rejected: bool = False
    host: str
    http_port: int
    socks_port: int
    username: str
    password: str


class TimeSlot(BaseModel):
    start: str
    end: str


class ScheduleProfile(BaseModel):
    name_fr: str
    proxy_id: str
    slots_by_day: dict[str, list[TimeSlot]]


class ScheduleProfiles(BaseModel):
    profiles: dict[str, ScheduleProfile]


class PersistedProxy(ProxyConfig):
    operation_timestamps: list[float] = Field(default_factory=list[float])
    register_cooldown_until: float | None = None


class ProxiesFile(BaseModel):
    proxies: dict[str, PersistedProxy] = Field(default_factory=dict[str, PersistedProxy])
