import argparse
import signal
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from types import FrameType
from zipfile import ZipFile

from dotenv import load_dotenv

from project_paths import BUNDLE_ROOT, IS_PACKAGED, PROJECT_ROOT, ensure_packaged_runtime_data

for import_root in (
    PROJECT_ROOT,
    PROJECT_ROOT / "DBDofusUnity",
    PROJECT_ROOT / "AnkamaLauncherEmulatorPremium",
):
    sys.path.insert(0, str(import_root))

from src.utils.runtime_paths import configure_project_import_paths

configure_project_import_paths()

from src.services.logging_utils.loggers import configure_root_logger


@dataclass(frozen=True)
class RuntimeArgs:
    use_bot_config_json: bool
    enable_automatic_schedules: bool
    headless: bool
    validate_install: bool
    application_argv: list[str]


def parse_runtime_args(argv: list[str]) -> RuntimeArgs:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--auto",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use resources/bots.json to configure bots at runtime.",
    )
    parser.add_argument(
        "--validate-install",
        action="store_true",
        help="Verify packaged resources and exit without starting the bot.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run bots without creating the GUI window.",
    )
    runtime_args, remaining_args = parser.parse_known_args(argv[1:])
    if runtime_args.headless and not runtime_args.auto:
        parser.error("--no-auto cannot be used with --headless")
    return RuntimeArgs(
        use_bot_config_json=runtime_args.auto,
        enable_automatic_schedules=runtime_args.auto,
        headless=runtime_args.headless,
        validate_install=runtime_args.validate_install,
        application_argv=[argv[0], *remaining_args],
    )


load_dotenv()

from src.controller.bot_config import BotConfigService  # noqa: E402
from src.core.bot.bot_manager import BotManager  # noqa: E402
from src.core.bot.lifecycle.scheduler import run_continuously  # noqa: E402
from src.core.signals.shared_farm_signals import SharedSignals  # noqa: E402


def _create_runtime(shared_signals: SharedSignals, enable_account_scheduler: bool) -> BotManager:
    bot_manager = BotManager(
        shared_signals=shared_signals,
        enable_account_scheduler=enable_account_scheduler,
    )
    bot_manager.ankama_launcher.start()

    return bot_manager


def _check_updated_mapping_resources() -> None:
    if IS_PACKAGED:
        return
    from DBDofusUnity.proto_mapper_assembly.scripts.dump import check_updated_mapping_resources

    check_updated_mapping_resources()


def _start_bots(bot_manager: BotManager, enable_automatic_schedules: bool) -> None:
    if not enable_automatic_schedules:
        return
    for bot in bot_manager.bot_by_account_id.values():
        bot.start()


def _shutdown_runtime(
    bot_manager: BotManager,
    cease_running: threading.Event,
    on_finished: Callable[[], None],
) -> None:
    cease_running.set()

    def shutdown() -> None:
        try:
            bot_manager.shutdown()
        finally:
            on_finished()

    threading.Thread(target=shutdown, name="bot-manager-shutdown").start()


def run_gui(application_argv: list[str], enable_automatic_schedules: bool) -> int:
    from PyQt6.QtCore import Qt
    from qfluentwidgets import Theme, setTheme, setThemeColor

    from src.gui.application import Application
    from src.gui.main_window import MainWindow

    application = Application(application_argv)
    shared_signals = SharedSignals()
    main_window = MainWindow(title=application.TITLE, shared_signals=shared_signals)
    main_window.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)

    bot_manager = _create_runtime(
        shared_signals,
        enable_account_scheduler=enable_automatic_schedules,
    )
    main_window.init_accounts(bot_manager.bot_by_account_id)
    main_window.splashScreen.finish()
    _start_bots(bot_manager, enable_automatic_schedules)
    cease_running = run_continuously()

    def on_app_close() -> None:
        _shutdown_runtime(
            bot_manager,
            cease_running,
            shared_signals.shutdown_finished.emit,
        )

    shared_signals.closed.connect(on_app_close)

    return application.exec()


def run_headless(application_argv: list[str], enable_automatic_schedules: bool) -> int:
    from PyQt6.QtCore import QCoreApplication, QTimer

    application = QCoreApplication(application_argv)
    shared_signals = SharedSignals()
    bot_manager = _create_runtime(
        shared_signals,
        enable_account_scheduler=enable_automatic_schedules,
    )
    _start_bots(bot_manager, enable_automatic_schedules)
    cease_running = run_continuously()
    shutdown_requested = threading.Event()

    def request_shutdown() -> None:
        if shutdown_requested.is_set():
            return
        shutdown_requested.set()
        _shutdown_runtime(bot_manager, cease_running, application.quit)

    def handle_signal(_signum: int, _frame: FrameType | None) -> None:
        QTimer.singleShot(0, request_shutdown)

    signal.signal(signal.SIGINT, handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_signal)

    return application.exec()


def main(argv: list[str] | None = None) -> int:
    runtime_args = parse_runtime_args(sys.argv if argv is None else argv)
    if runtime_args.validate_install:
        required_paths = (
            BUNDLE_ROOT / "resources" / "icons" / "logo.png",
            BUNDLE_ROOT / "DBDofusUnity" / "datas" / "bundles" / "data" / "SubAreasDataRoot.json",
            BUNDLE_ROOT / "DBDofusUnity" / "datas" / "bundles" / "i18n.json",
            BUNDLE_ROOT / "DBDofusUnity" / "datas" / "bundles" / "maps.zip",
            BUNDLE_ROOT / "DBDofusUnity" / "datas" / "bundles" / "standalone" / "world-graph.json",
        )
        missing_paths = [str(path) for path in required_paths if not path.is_file()]
        if missing_paths:
            raise RuntimeError(f"Missing packaged resources: {', '.join(missing_paths)}")
        maps_archive_path = BUNDLE_ROOT / "DBDofusUnity" / "datas" / "bundles" / "maps.zip"
        with ZipFile(maps_archive_path) as archive:
            invalid_map_path = archive.testzip()
            if invalid_map_path is not None:
                raise RuntimeError(f"Invalid map archive entry: {invalid_map_path}")
        return 0
    _check_updated_mapping_resources()

    ensure_packaged_runtime_data()
    BotConfigService.use_bot_config_json = runtime_args.use_bot_config_json

    configure_root_logger()

    if runtime_args.headless:
        return run_headless(
            runtime_args.application_argv,
            runtime_args.enable_automatic_schedules,
        )
    return run_gui(
        runtime_args.application_argv,
        runtime_args.enable_automatic_schedules,
    )


if __name__ == "__main__":
    raise SystemExit(main())
