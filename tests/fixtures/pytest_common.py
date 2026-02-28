import os
import tempfile
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, Protocol, cast
from unittest.mock import MagicMock

import pytest
import requests
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.credentials import StoredApiKey
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.zaap_files import GameSubscription
from DBDofusUnity.proto_mapper_assembly.runtime import runtime_store
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

from src.consts import MIN_DATE
from src.core.bot.bot import Bot
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.bot.lifecycle.scheduler import BotScheduler
from src.core.states.guild_chest_storage import GuildChestStorage
from src.protocol import protocol_game
from src.services.debug_recorder import DebugRecorder
from tests.fixtures.accounts import make_account, make_runtime_bot
from tests.fixtures.bot_runtime import make_behavior_coordinator, make_bot_scheduler
from tests.fixtures.game_state import GameStateContext, make_game_state_ctx
from tests.fixtures.storage import make_guild_chest_storage


class _PreparedRequest(Protocol):
    url: str | None


@pytest.fixture
def behavior_coordinator() -> BehaviorCoordinator:
    return make_behavior_coordinator()


@pytest.fixture
def bot_scheduler() -> BotScheduler:
    return make_bot_scheduler()


@pytest.fixture(autouse=True)
def logger(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> MagicMock:
    monkeypatch.setattr("src.consts.BOT_DEBUG_LOGS_DIR", tmp_path)
    return MagicMock()


@pytest.fixture(autouse=True)
def _isolate_resource_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.paysafecard_pool.PAYSAFECARDS_PATH", tmp_path / "paysafecards.txt")
    monkeypatch.setattr("AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.paysafecard_purchase.PAYSAFECARD_PURCHASE_PATH", tmp_path / "paysafecard_purchase.local.json")
    monkeypatch.setattr("src.services.user_activity.USER_ACTIVITY_PATH", tmp_path / "user_activity.json")


@pytest.fixture(autouse=True)
def _block_smailpro_network(monkeypatch: pytest.MonkeyPatch) -> None:
    original_send = cast(Callable[..., requests.Response], getattr(requests.Session, "send"))

    def send(session: requests.Session, request: _PreparedRequest, **kwargs: Any) -> requests.Response:
        if request.url is not None and request.url.startswith("https://app.sonjj.com/"):
            raise AssertionError("Tests must mock SmailPro requests; live API calls consume credits")
        return original_send(session, request, **kwargs)

    monkeypatch.setattr(requests.Session, "send", send)


@pytest.fixture(autouse=True)
def game_sub_info_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_game_sub_info(login: str) -> GameSubscription:
        return GameSubscription(isFreeToPlay=True, isFormerSubscriber=False, isSubscribed=False, totalPlayTime=0, endOfSubscribe=MIN_DATE, id=1)

    monkeypatch.setattr("src.core.states.player_state.get_game_sub_info_by_login", fake_get_game_sub_info)


@pytest.fixture
def tmp_json_path(tmp_path: Path) -> Path:
    return tmp_path / f"{uuid.uuid4()}.json"


@pytest.fixture
def runtime_data_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[RuntimeDataStore]:
    monkeypatch.setattr(runtime_store, "RUNTIME_DATA_FILE", tmp_path / "instancied_msg_infos.json")
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
def game_state_ctx(_shared_game_state_debug_recorder: DebugRecorder) -> GameStateContext:
    return make_game_state_ctx(_shared_game_state_debug_recorder)


@pytest.fixture(scope="session")
def _shared_game_state_debug_recorder() -> Iterator[DebugRecorder]:
    recorder = DebugRecorder(file_path=os.path.join(tempfile.gettempdir(), "gamestatefixture.debug.jsonl"))
    yield recorder
    recorder.stop()


@pytest.fixture
def runtime_bot(game_sub_info_mock: None) -> Iterator[Bot]:
    bot = make_runtime_bot("TEST", 1)
    yield bot
    bot.watchdog.stop()
    bot.debug_recorder.stop()


@pytest.fixture
def guild_chest_storage() -> GuildChestStorage:
    return make_guild_chest_storage()
