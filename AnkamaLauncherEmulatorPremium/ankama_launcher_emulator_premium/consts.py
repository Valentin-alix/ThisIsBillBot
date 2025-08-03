import os
import re
import shutil
from pathlib import Path

from dotenv import load_dotenv
from project_paths import ENV_PATH

load_dotenv(ENV_PATH)
LAUNCHER_PORT = 26116
RETRO_TEXT_SOCKET_PORT = 26117


RESOURCES = Path(__file__).parent.parent / "resources"
BOTS_STORAGE_PATH = RESOURCES / "bots.local.json"
PROXIES_STORAGE_PATH = RESOURCES / "proxies.local.json"
SCHEDULE_PROFILES_PATH = RESOURCES / "schedule_profiles.json"
PAYSAFECARDS_PATH = RESOURCES / "paysafecards.txt"
PAYSAFECARD_PURCHASE_PATH = RESOURCES / "paysafecard_purchase.local.json"
DEBUG_DIR = RESOURCES / "debug"
BOT_DEBUG_LOGS_DIR = DEBUG_DIR / "bots"
DEBUG_DUMPS_DIR = DEBUG_DIR / "dumps"

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

CYTRUS_INSTALLED = shutil.which("cytrus-v6") is not None


ASAR_PATH = Path(os.getenv("programfiles", "")) / "Ankama" / "Ankama Launcher" / "resources" / "app.asar"
