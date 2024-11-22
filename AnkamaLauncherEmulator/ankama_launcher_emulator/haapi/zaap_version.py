import json
import os
from functools import cache

import requests

CYTRUS_URL = "https://cytrus.cdn.ankama.com/cytrus.json"


@cache
def get_client_version() -> str:
    response = requests.get(CYTRUS_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["games"]["dofus"]["assets"]["main"]["latest"]


def get_zaap_version():
    filename = "package.json"
    try:
        os.system(
            f'asar extract-file "{os.path.join(os.getenv("programfiles", ""), "Ankama", "Ankama Launcher", "resources", "app.asar")}" "{filename}"'
        )
        zaapVersion = "none"
        if os.path.exists(filename):
            with open(filename) as jsonFile:
                disctJson = json.load(jsonFile)
                zaapVersion = disctJson.get("version")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

    if zaapVersion == "none":
        zaapVersion = "3.12.19"

    return zaapVersion


ZAAP_VERSION = get_zaap_version()
