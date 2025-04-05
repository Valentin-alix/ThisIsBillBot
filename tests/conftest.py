import uuid
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock

import pytest
from ankama_launcher_emulator_premium.interfaces.credentials import (
    StoredApiKey,
)
from proto_mapper_assembly.runtime import runtime_store
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

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
    monkeypatch.setattr("src.const.LOG_FOLDER", tmp_path)
    return MagicMock()


@pytest.fixture
def tmp_json_path(tmp_path: Path) -> Path:
    return tmp_path / f"{uuid.uuid4()}.json"


@pytest.fixture
def runtime_data_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[RuntimeDataStore]:
    monkeypatch.setattr(runtime_store, "PC_ID", "test")
    monkeypatch.setattr(runtime_store, "RUNTIME_DATA_DIR", tmp_path)
    instance = RuntimeDataStore()
    monkeypatch.setattr(protocol_game, "_on_exit", lambda: None)
    yield instance
    del instance._writing_content
    instance.path.unlink(missing_ok=True)


@pytest.fixture
def account() -> StoredApiKey:
    return make_account("TestBot", 1)


@pytest.fixture
def game_state_ctx() -> GameStateContext:
    return make_game_state_ctx()


@pytest.fixture
def runtime_bot() -> Bot:
    return make_runtime_bot("TEST", 1)


@pytest.fixture
def guild_chest_storage() -> GuildChestStorage:
    return make_guild_chest_storage()
