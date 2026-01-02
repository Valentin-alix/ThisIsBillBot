import asyncio
import logging
import sys
from dataclasses import replace
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import SONJI_API_KEY
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.smailpro import (
    SmailProMailProvider,
    generate_random_mailbox_settings,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.identity import (
    DEFAULT_PASSWORD,
    random_identity,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.models import RegistrationOptions
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.registration import (
    register_account,
)


async def _register_one() -> bool:
    api_key = SONJI_API_KEY
    if api_key is None:
        raise RuntimeError("SONJI_API_KEY must be set to run a registration debug attempt")

    async def create_mail_provider() -> tuple[str, SmailProMailProvider]:
        settings = await asyncio.to_thread(generate_random_mailbox_settings, api_key)
        return settings.email, SmailProMailProvider(settings)

    async def replacement_options_factory(options: RegistrationOptions) -> RegistrationOptions:
        email, mail_provider = await create_mail_provider()
        logging.info("[Register debug] Using replacement mailbox %s", email)
        return replace(
            options,
            email=email,
            mail_provider=mail_provider,
        )

    email, mail_provider = await create_mail_provider()
    logging.info("[Register debug] Using fresh mailbox %s", email)
    result = await register_account(
        RegistrationOptions(
            email=email,
            password=DEFAULT_PASSWORD,
            identity=random_identity(),
            mail_provider=mail_provider,
            persist_account=False,
        ),
        replacement_options_factory=replacement_options_factory,
    )
    logging.info(
        "[Register debug] success=%s email=%s password=%s final_url=%s error=%s antibot_marker=%s",
        result.success,
        result.email,
        result.password,
        result.final_url,
        result.error,
        result.antibot_marker,
    )
    return result.success


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    raise SystemExit(0 if asyncio.run(_register_one()) else 1)


if __name__ == "__main__":
    main()
