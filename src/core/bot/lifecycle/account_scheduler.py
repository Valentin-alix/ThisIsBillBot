import asyncio
import logging
import threading
from dataclasses import dataclass, field

import schedule
from ankama_launcher_emulator_premium.web.auth.launcher_login import (
    authenticate_available_accounts,
)
from ankama_launcher_emulator_premium.web.auth.registration import (
    register_available_emails,
)

logger = logging.getLogger()

DAILY_AUTH_RUN_AT = "09:00"
DAILY_REGISTER_RUN_AT = "10:00"


@dataclass
class AccountScheduler:
    _job_auth: schedule.Job | None = field(init=False, default=None)
    _job_register: schedule.Job | None = field(init=False, default=None)

    def start(self) -> None:
        assert self._job_auth is None, "Scheduler is already started"
        self._job_auth = (
            schedule.every().day.at(DAILY_AUTH_RUN_AT).do(self._do_authentication)
        )
        self._job_register = (
            schedule.every().day.at(DAILY_REGISTER_RUN_AT).do(self._do_registration)
        )
        logger.info(
            f"Account auth & register scheduler armed daily at {DAILY_AUTH_RUN_AT} & {DAILY_REGISTER_RUN_AT}"
        )

    def _do_authentication(self):
        def run_auth():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(authenticate_available_accounts())
            finally:
                loop.close()

        threading.Thread(target=run_auth).start()

    def _do_registration(self):
        def run_register():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(register_available_emails())
            finally:
                loop.close()

        threading.Thread(target=run_register).start()

    def stop(self) -> None:
        assert self._job_auth is not None, "Auth scheduler is not started"
        schedule.cancel_job(self._job_auth)
        self._job_auth = None

        assert self._job_register is not None, "Register scheduler is not started"
        schedule.cancel_job(self._job_register)
        self._job_register = None
