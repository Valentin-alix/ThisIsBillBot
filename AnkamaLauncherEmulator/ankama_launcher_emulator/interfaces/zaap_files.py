from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GameSubscription(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_free_to_play: bool = Field(alias="isFreeToPlay", serialization_alias="isFreeToPlay")
    is_former_subscriber: bool = Field(alias="isFormerSubscriber", serialization_alias="isFormerSubscriber")
    is_subscribed: bool = Field(alias="isSubscribed", serialization_alias="isSubscribed")
    total_play_time: int = Field(alias="totalPlayTime", serialization_alias="totalPlayTime")
    end_of_subscribe: datetime | None = Field(alias="endOfSubscribe", serialization_alias="endOfSubscribe")
    id: int


class UserAccount(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    login: str
    nickname: str | None
    id: int
    type: Literal["ANKAMA"]
    firstname: str
    lastname: str
    tag: str | None
    security: list[str]
    locked: str
    game_list: list[GameSubscription] = Field(
        alias="gameList",
        serialization_alias="gameList",
        default_factory=list[GameSubscription],
    )
