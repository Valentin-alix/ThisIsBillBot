"""Global daily job that auto-subscribes every account flagged with
``BotConfig.auto_subscribe``.

Registered once on ``BotManager`` startup; relies on the existing
``run_continuously`` thread (started from ``__main__``) to tick the
``schedule`` library.
"""

import logging
import random
import time
from dataclasses import dataclass, field

import schedule
from ankama_launcher_emulator_premium.web.subscription.models import (
    SubscribeOptions,
)
from ankama_launcher_emulator_premium.web.subscription.service import (
    SubscribeService,
    _build_subscribe_service,
)

from src.controller.bot_config import BotConfigController

logger = logging.getLogger()

DAILY_RUN_AT = "06:00"
MIN_DELAY_BETWEEN_ACCOUNTS_SEC = 30
MAX_DELAY_BETWEEN_ACCOUNTS_SEC = 90


@dataclass
class SubscriptionScheduler:
    bot_config_controller: BotConfigController = field(
        default_factory=BotConfigController
    )
    subscribe_service: SubscribeService = field(
        default_factory=_build_subscribe_service
    )
    _job: schedule.Job | None = field(init=False, default=None)

    def start(self) -> None:
        assert self._job is None, "Scheduler is already started"
        self._job = schedule.every().day.at(DAILY_RUN_AT).do(self._tick)
        logger.info(f"Subscription scheduler armed daily at {DAILY_RUN_AT}")

    def stop(self) -> None:
        assert self._job is not None, "Scheduler is not started"
        schedule.cancel_job(self._job)
        self._job = None

    def _tick(self) -> None:
        configs = self.bot_config_controller.get_bot_config_by_login()
        targets = [
            (login, config)
            for login, config in configs.items()
            if config.auto_subscribe
        ]
        if not targets:
            return

        logger.info(f"Subscription tick: {len(targets)} account(s) to check")
        for index, (login, config) in enumerate(targets):
            options = SubscribeOptions(proxy=config.subscribe_proxy)
            result = self.subscribe_service.run(login, options)
            logger.info(f"[{login}] {result}")
            if index < len(targets) - 1:
                time.sleep(
                    random.uniform(
                        MIN_DELAY_BETWEEN_ACCOUNTS_SEC,
                        MAX_DELAY_BETWEEN_ACCOUNTS_SEC,
                    )
                )
