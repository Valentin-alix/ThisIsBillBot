import uuid
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from ankama_launcher_emulator_premium.interfaces.credentials import (
    StoredApiKey,
)
from ankama_launcher_emulator_premium.interfaces.zaap_files import GameSubscription
from proto_mapper_assembly.runtime import runtime_store
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

from src.const import MIN_DATE
from src.core.bot.bot import Bot
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.bot.lifecycle.scheduler import BotScheduler
from src.core.states.guild_chest_storage import GuildChestStorage
from src.protocol import protocol_game
from tests.fixtures.accounts import (
    make_account,
    make_runtime_bot,
)
from tests.fixtures.bot_runtime import (
    make_behavior_coordinator,
    make_bot_scheduler,
)
from tests.fixtures.game_state import (
    GameStateContext,
    make_game_state_ctx,
)
from tests.fixtures.storage import (
    make_guild_chest_storage,
)


@pytest.fixture
def behavior_coordinator() -> BehaviorCoordinator:
    return make_behavior_coordinator()


@pytest.fixture
def bot_scheduler() -> BotScheduler:
    return make_bot_scheduler()


@pytest.fixture(autouse=True)
def logger(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> MagicMock:
    monkeypatch.setattr("ankama_launcher_emulator_premium.consts.BOT_DEBUG_LOGS_DIR", tmp_path)
    return MagicMock()


@pytest.fixture(autouse=True)
def _isolate_resource_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "src.core.behaviors.account.paysafecard_subscription.PAYSAFECARDS_PATH",
        tmp_path / "paysafecards.txt",
    )
    monkeypatch.setattr(
        "src.core.behaviors.account.paysafecard_subscription.PAYSAFECARD_PURCHASE_PATH",
        tmp_path / "paysafecard_purchase.local.json",
    )
    monkeypatch.setattr(
        "src.core.bot.lifecycle.connection_handler.PAYSAFECARDS_PATH",
        tmp_path / "paysafecards.txt",
    )
    monkeypatch.setattr(
        "src.core.bot.lifecycle.connection_handler.PAYSAFECARD_PURCHASE_PATH",
        tmp_path / "paysafecard_purchase.local.json",
    )
    monkeypatch.setattr(
        "ankama_launcher_emulator_premium.web.debug_utils.DEBUG_DUMPS_DIR",
        tmp_path / "debug" / "dumps",
    )
    monkeypatch.setattr(
        "ankama_launcher_emulator_premium.web.subscription.xsolla_paysafecard.DEBUG_DUMPS_DIR",
        tmp_path / "debug" / "dumps",
    )


@pytest.fixture(autouse=True)
def game_sub_info_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_game_sub_info(login: str):
        return GameSubscription(
            isFreeToPlay=True,
            isFormerSubscriber=False,
            isSubscribed=False,
            totalPlayTime=0,
            endOfSubscribe=MIN_DATE,
            id=1,
        )

    monkeypatch.setattr(
        "src.core.states.player_state.get_game_sub_info_by_login",
        fake_get_game_sub_info,
    )


@pytest.fixture
def tmp_json_path(tmp_path: Path) -> Path:
    return tmp_path / f"{uuid.uuid4()}.json"


@pytest.fixture
def runtime_data_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[RuntimeDataStore]:
    monkeypatch.setattr(runtime_store, "RUNTIME_DATA_DIR", tmp_path)
    instance = RuntimeDataStore()
    instance._capture_target_path = None  # pyright: ignore[reportPrivateUsage]
    monkeypatch.setattr(protocol_game, "_on_exit", lambda: None)
    yield instance
    instance.path.unlink(missing_ok=True)
    del instance._writing_content
    instance._capture_target_path = None  # pyright: ignore[reportPrivateUsage]


@pytest.fixture
def account() -> StoredApiKey:
    return make_account("TestBot", 1)


@pytest.fixture
def game_state_ctx() -> GameStateContext:
    return make_game_state_ctx()


@pytest.fixture
def runtime_bot(game_sub_info_mock: None) -> Bot:
    return make_runtime_bot("TEST", 1)


@pytest.fixture
def guild_chest_storage() -> GuildChestStorage:
    return make_guild_chest_storage()
