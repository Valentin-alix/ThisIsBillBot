import os
import re
import shutil
from pathlib import Path

from dotenv import load_dotenv

from project_paths import ENV_PATH

load_dotenv(ENV_PATH)
LAUNCHER_PORT = 26116


RESOURCES = Path(__file__).parent.parent / "resources"
BOTS_STORAGE_PATH = RESOURCES / "bots.local.json"
PROXIES_STORAGE_PATH = RESOURCES / "proxies.json"
SCHEDULE_PROFILES_PATH = RESOURCES / "schedule_profiles.json"
MAIL_ACCOUNTS_STORAGE_PATH = RESOURCES / "mail_accounts.json"
PAYSAFECARDS_PATH = RESOURCES / "paysafecards.txt"
PAYSAFECARD_PURCHASE_PATH = RESOURCES / "paysafecard_purchase.local.json"
DEBUG_DIR = RESOURCES / "debug"
DEBUG_DUMPS_DIR = DEBUG_DIR / "dumps"

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

CYTRUS_INSTALLED = shutil.which("cytrus-v6") is not None


ASAR_PATH = Path(os.getenv("programfiles", "")) / "Ankama" / "Ankama Launcher" / "resources" / "app.asar"
