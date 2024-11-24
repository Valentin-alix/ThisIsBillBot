import json
import logging
import os
from typing import TypedDict

from ankama_launcher_emulator.consts import ACCOUNTS_PATH, EMAILS_PATH

logger = logging.getLogger()


class Account(TypedDict):
    email: str
    password: str


def load_accounts() -> list[Account]:
    if not os.path.exists(ACCOUNTS_PATH):
        return []
    try:
        with open(ACCOUNTS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def load_emails() -> list[str]:
    if not EMAILS_PATH or not os.path.exists(EMAILS_PATH):
        return []
    try:
        with open(EMAILS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def load_unregistered_accounts(stored_accounts: list) -> list[Account]:
    """Return accounts from generated_accounts.json not yet stored locally."""
    accounts = load_accounts()
    stored_logins = {acc["apikey"]["login"] for acc in stored_accounts}
    return [acc for acc in accounts if acc.get("email") not in stored_logins]


def save_account(email: str, password: str) -> None:
    os.makedirs(os.path.dirname(ACCOUNTS_PATH), exist_ok=True)
    if os.path.exists(ACCOUNTS_PATH):
        with open(ACCOUNTS_PATH, "r", encoding="utf-8") as f:
            accounts = json.load(f)
    else:
        accounts = []
    accounts.append({"email": email, "password": password})
    with open(ACCOUNTS_PATH, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)
    logger.info("[Register] Account saved to %s", ACCOUNTS_PATH)
