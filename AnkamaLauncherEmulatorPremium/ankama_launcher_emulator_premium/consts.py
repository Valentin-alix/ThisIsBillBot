import os
import re
import shutil
from pathlib import Path

from dotenv import load_dotenv

from project_paths import ENV_PATH, USER_DATA_ROOT

load_dotenv(ENV_PATH)
LAUNCHER_PORT = 26116


RESOURCES = USER_DATA_ROOT / "AnkamaLauncherEmulatorPremium" / "resources"
BOTS_STORAGE_PATH = RESOURCES / "bots.json"
PROXIES_STORAGE_PATH = RESOURCES / "proxies.json"
SCHEDULE_PROFILES_PATH = RESOURCES / "schedule_profiles.json"
MAIL_ACCOUNTS_STORAGE_PATH = RESOURCES / "mail_accounts.json"
SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH = RESOURCES / "smailpro_outlook_disabled_until.json"
PAYSAFECARDS_PATH = RESOURCES / "paysafecards.txt"
PAYSAFECARD_PURCHASE_PATH = RESOURCES / "paysafecard_purchase.local.json"
DEBUG_DIR = RESOURCES / "debug"
DEBUG_TRACES_DIR = DEBUG_DIR / "traces"

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

CYTRUS_INSTALLED = shutil.which("cytrus-v6") is not None


ASAR_PATH = Path(os.getenv("programfiles", "")) / "Ankama" / "Ankama Launcher" / "resources" / "app.asar"
ZAAP_PATH = Path(os.environ["APPDATA"]) / "zaap"

SONJI_API_KEY = os.getenv("SONJI_API_KEY")
