import json
import os

if os.name == "nt":
    ZAAP_PATH = os.path.join(os.environ["APPDATA"], "zaap")
else:
    config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    ZAAP_PATH = os.path.join(config_home, "zaap")

RELEASE_JSON_PATH = os.path.join(
    ZAAP_PATH, "repositories", "production", "dofus", "dofus3", "release.json"
)
if os.path.exists(RELEASE_JSON_PATH):
    with open(RELEASE_JSON_PATH, "r") as file:
        content = json.load(file)
        DOFUS_PATH = os.path.join(content["location"], "Dofus.exe")
else:
    DOFUS_PATH = "DUMMY_PATH"
    print("<!> No Dofus path found !")


CERTIFICATE_FOLDER_PATH = os.path.join(ZAAP_PATH, "certificate")
API_KEY_FOLDER_PATH = os.path.join(ZAAP_PATH, "keydata")
OFFICIAL_CONFIG_URL = r"https://dofus2.cdn.ankama.com/config/dofus3.json"


SETTINGS_PATH = os.path.join(ZAAP_PATH, "Settings")

BASE_CONFIG_URL = "https://dofus2.cdn.ankama.com/config/dofus3.json"
