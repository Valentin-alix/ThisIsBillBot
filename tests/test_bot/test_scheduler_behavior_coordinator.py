import importlib.util
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path
from threading import Event, RLock
from types import SimpleNamespace
from unittest.mock import Mock, patch

import schedule

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module_from_path(
    module_name: str, relative_path: str, stub_modules: dict[str, types.ModuleType]
) -> types.ModuleType:
    module_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {module_name} from {module_path}")

    loaded_module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, stub_modules):
        sys.modules[module_name] = loaded_module
        spec.loader.exec_module(loaded_module)
    return loaded_module


def _build_behavior_coordinator_stubs() -> dict[str, types.ModuleType]:
    def run_in_background(
        func: object,
        on_success: object | None = None,
        on_error: object | None = None,
        on_progress: object | None = None,
        parent: object | None = None,
    ) -> None:
        del func, on_success, on_error, on_progress, parent

    gui_utils_module = types.ModuleType("ankama_launcher_emulator_premium.gui.utils")
    setattr(gui_utils_module, "run_in_background", run_in_background)

    interfaces_module = types.ModuleType(
        "ankama_launcher_emulator_premium.interfaces.deciphered_api_key"
    )
    setattr(interfaces_module, "DecipheredApiKey", dict)

    recipe_module = types.ModuleType("dofus_unity_reader.models.datas.recipe_root")
    setattr(recipe_module, "RecipeItem", object)

    controller_module = types.ModuleType("src.controller.bot_config")
    setattr(controller_module, "BotConfig", object)

    @dataclass
    class ContextualLogger:
        _logger: object

        @property
        def logger(self) -> object:
            return self._logger

    contextual_logger_module = types.ModuleType("src.services.logging.contextual_logger")
    setattr(contextual_logger_module, "ContextualLogger", ContextualLogger)

    class FakeBehavior:
        state: object = None

        def stop(self) -> None:
            return None

    behavior_module = types.ModuleType("src.core.behaviors.behavior")
    setattr(behavior_module, "Behavior", FakeBehavior)
    setattr(
        behavior_module,
        "BehaviorState",
        SimpleNamespace(RUNNING="RUNNING"),
    )

    config_module = types.ModuleType("src.core.config")
    setattr(config_module, "MULE_BANK_CHARACTER_LOGIN", [])

    event_manager_module = types.ModuleType("src.core.events_manager.event_manager")
    setattr(event_manager_module, "EventManager", object)

    bot_signals_module = types.ModuleType("src.core.signals.bot_signals")
    setattr(bot_signals_module, "BotSignals", object)

    shared_signals_module = types.ModuleType("src.core.signals.shared_farm_signals")
    setattr(shared_signals_module, "SharedSignals", object)

    behavior_module_names = {
        "src.core.behaviors.craft.craft_behavior": "CraftBehavior",
        "src.core.behaviors.farms.auto_bot_behavior": "AutoBotBehavior",
        "src.core.behaviors.farms.fight.fight_behavior": "FightBehavior",
        "src.core.behaviors.farms.fighter_behavior": "FighterBehavior",
        "src.core.behaviors.farms.harvester_behavior": "HarvesterBehavior",
        "src.core.behaviors.mule_storage.mule_accept_behavior": "MuleAcceptBehavior",
    }

    stub_modules: dict[str, types.ModuleType] = {
        "ankama_launcher_emulator_premium.gui.utils": gui_utils_module,
        "ankama_launcher_emulator_premium.interfaces.deciphered_api_key": interfaces_module,
        "dofus_unity_reader.models.datas.recipe_root": recipe_module,
        "src.controller.bot_config": controller_module,
        "src.services.logging.contextual_logger": contextual_logger_module,
        "src.core.behaviors.behavior": behavior_module,
        "src.core.config": config_module,
        "src.core.events_manager.event_manager": event_manager_module,
        "src.core.signals.bot_signals": bot_signals_module,
        "src.core.signals.shared_farm_signals": shared_signals_module,
    }

    for module_name, class_name in behavior_module_names.items():
        behavior_child_module = types.ModuleType(module_name)
        setattr(behavior_child_module, class_name, FakeBehavior)
        stub_modules[module_name] = behavior_child_module

    return stub_modules


def _build_scheduler_stubs() -> dict[str, types.ModuleType]:
    def run_in_background(
        func: object,
        on_success: object | None = None,
        on_error: object | None = None,
        on_progress: object | None = None,
        parent: object | None = None,
    ) -> None:
        del func, on_success, on_error, on_progress, parent

    gui_utils_module = types.ModuleType("ankama_launcher_emulator_premium.gui.utils")
    setattr(gui_utils_module, "run_in_background", run_in_background)

    interfaces_module = types.ModuleType(
        "ankama_launcher_emulator_premium.interfaces.deciphered_api_key"
    )
    setattr(interfaces_module, "DecipheredApiKey", dict)

    @dataclass
    class BotConfig:
        schedule_profile: str | None = None

    controller_module = types.ModuleType("src.controller.bot_config")
    setattr(controller_module, "BotConfig", BotConfig)

    class ScheduleProfileController:
        def get_profile(self, profile_id: str) -> object | None:
            del profile_id
            return None

    schedule_profile_module = types.ModuleType("src.controller.schedule_profile_controller")
    setattr(schedule_profile_module, "ScheduleProfileController", ScheduleProfileController)

    @dataclass
    class ContextualLogger:
        _logger: object

        @property
        def logger(self) -> object:
            return self._logger

    contextual_logger_module = types.ModuleType("src.services.logging.contextual_logger")
    setattr(contextual_logger_module, "ContextualLogger", ContextualLogger)

    behavior_coordinator_module = types.ModuleType(
        "src.core.bot.execution.behavior_coordinator"
    )
    setattr(behavior_coordinator_module, "BehaviorCoordinator", object)

    process_manager_module = types.ModuleType("src.core.bot.execution.process_manager")
    setattr(process_manager_module, "ProcessManager", object)

    bot_signals_module = types.ModuleType("src.core.signals.bot_signals")
    setattr(bot_signals_module, "BotSignals", object)

    shared_signals_module = types.ModuleType("src.core.signals.shared_farm_signals")
    setattr(shared_signals_module, "SharedSignals", object)

    log_signals_module = types.ModuleType("src.core.signals.log_signals")
    setattr(log_signals_module, "LogSignals", object)

    message_signals_module = types.ModuleType("src.core.signals.message_signals")
    setattr(message_signals_module, "MessageInfoSignals", object)

    internet_module = types.ModuleType("src.utils.internet")
    setattr(internet_module, "has_internet_connection", lambda: True)

    return {
        "ankama_launcher_emulator_premium.gui.utils": gui_utils_module,
        "ankama_launcher_emulator_premium.interfaces.deciphered_api_key": interfaces_module,
        "src.controller.bot_config": controller_module,
        "src.controller.schedule_profile_controller": schedule_profile_module,
        "src.services.logging.contextual_logger": contextual_logger_module,
        "src.core.bot.execution.behavior_coordinator": behavior_coordinator_module,
        "src.core.bot.execution.process_manager": process_manager_module,
        "src.core.signals.bot_signals": bot_signals_module,
        "src.core.signals.shared_farm_signals": shared_signals_module,
        "src.core.signals.log_signals": log_signals_module,
        "src.core.signals.message_signals": message_signals_module,
        "src.utils.internet": internet_module,
    }


class TestBehaviorCoordinator(unittest.TestCase):
    def test_on_play_harvester_emits_stop_signal_when_behavior_finishes(self) -> None:
        module = _load_module_from_path(
            "test_behavior_coordinator_module",
            "src/core/bot/execution/behavior_coordinator.py",
            _build_behavior_coordinator_stubs(),
        )
        coordinator_type = module.BehaviorCoordinator

        stop_emit = Mock()
        coordinator = coordinator_type(
            _logger=Mock(),
            is_connected_event=Event(),
            is_ready_to_play_event=Event(),
            is_playing_event=Event(),
            from_manual_play=Event(),
            event_manager=SimpleNamespace(lock=RLock()),
            fight_behavior=Mock(),
            harvester_behavior=Mock(),
            fighter_behavior=Mock(),
            craft_behavior=Mock(),
            mule_accept_kamas_behavior=Mock(),
            auto_bot_behavior=Mock(),
            usable_behaviors=[],
            bot_signals=SimpleNamespace(
                stop=SimpleNamespace(emit=stop_emit),
                play=SimpleNamespace(emit=Mock()),
                play_mule_kamas=SimpleNamespace(emit=Mock()),
                play_auto_bot=SimpleNamespace(emit=Mock()),
            ),
            shared_signals=SimpleNamespace(launch_account=SimpleNamespace(emit=Mock())),
            account={"apikey": {"login": "test-login"}},
            get_bot_config=Mock(return_value=None),
        )
        coordinator.stop_behaviors = Mock()

        coordinator.on_play_harvester(area_id=11, sub_area_id=22)

        self.assertIsNotNone(coordinator._current_bot_action_func)

        def progress_callback(_message: str) -> None:
            return None

        coordinator._current_bot_action_func(progress_callback)

        start_call = coordinator.harvester_behavior.start.call_args
        self.assertIsNotNone(start_call)
        callback = start_call.kwargs["callback"]
        self.assertEqual(start_call.kwargs["area_id"], 11)
        self.assertEqual(start_call.kwargs["sub_area_id"], 22)

        callback("finished")

        stop_emit.assert_called_once_with()


class TestBotScheduler(unittest.TestCase):
    def tearDown(self) -> None:
        schedule.clear()

    def test_schedule_profile_jobs_store_schedule_jobs(self) -> None:
        module = _load_module_from_path(
            "test_scheduler_module",
            "src/core/bot/lifecycle/scheduler.py",
            _build_scheduler_stubs(),
        )
        scheduler_type = module.BotScheduler

        schedule.clear()
        bot_scheduler = scheduler_type(
            _logger=Mock(),
            account={"apikey": {"login": "test-login"}},
            bot_signals=SimpleNamespace(
                play=SimpleNamespace(emit=Mock()),
                stop=SimpleNamespace(emit=Mock()),
            ),
            shared_signals=SimpleNamespace(launch_account=SimpleNamespace(emit=Mock())),
            log_signals=Mock(),
            is_playing_event=Event(),
            msg_info_signals=Mock(),
            get_bot_config=Mock(return_value=None),
            behavior_coordinator=Mock(),
            process_manager=Mock(),
        )
        profile = SimpleNamespace(
            slots_by_day={"0": [SimpleNamespace(start="10:00", end="11:00")]}
        )

        with patch.object(
            module.ScheduleProfileController, "get_profile", return_value=profile
        ), patch.object(module, "_add_random_minutes", return_value="10:03"), patch.object(
            module, "_subtract_random_minutes", return_value="10:57"
        ):
            bot_scheduler._schedule_profile_jobs("weekday")

        self.assertEqual(len(bot_scheduler._scheduled_jobs), 3)
        self.assertTrue(
            all(isinstance(job, schedule.Job) for job in bot_scheduler._scheduled_jobs)
        )

        bot_scheduler._clear_scheduled_jobs()

        self.assertEqual(bot_scheduler._scheduled_jobs, [])


if __name__ == "__main__":
    unittest.main()
