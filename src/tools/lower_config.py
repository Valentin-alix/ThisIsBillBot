import json
import os
from typing import Any

low_consumption_config = {
    "fps": {"value": 30},
    "vsync": {"value": False},
    "dofusQuality": {"value": 0},
    "antiAliasingMode": {"value": 0},
    "smaaQuality": {"value": 0},
    "msaaQuality": {"value": 0},
    "hdrEnabled": {"value": False},
    "currentTexturePack": {"value": 1},
    "allowMapEffects": {"value": False},
    "displayAuras": {"value": False},
    "alwaysShowAuraOnFront": {"value": False},
    "showEveryMonsters": {"value": False},
    "allowAnimShake": {"value": False},
    "maxEffectCount": {"value": 1},
    "isFightContextCache": {"value": True},
    "allowAnimsFun": {"value": False},
    "allowSpellEffects": {"value": False},
    "dialogAnimationEnabled": {"value": False},
    "animateFightPreviewTooltips": {"value": False},
    "turnPicture": {"value": False},
    "showDamagesPreview": {"value": False},
    "showMovePreview": {"value": False},
    "showMovementArea": {"value": False},
    "showMovementDistance": {"value": False},
    "displayTooltips": {"value": False},
    "showPermanentTargetsTooltips": {"value": False},
    "showItemTooltipDescription": {"value": False},
    "timelineShowSummonedFighters": {"value": False},
    "timelineShowDeadFighters": {"value": False},
    "timelineFollowPlayingEntity": {"value": False},
    "timelineShowFightersOrder": {"value": False},
    "creatureModeRoleplay": {"value": True},
    "creatureModeFight": {"value": True},
    "creaturesMode": {"value": 0},
    "showTurnsRemaining": {"value": False},
    "toggleEntityIcons": {"value": False},
    "pointsOverhead": {"value": 0},
    "showBreed": {"value": False},
    "spectatorAutoShowCurrentFighterInfo": {"value": False},
}


RELEASE_FOLDER = os.path.join(
    os.environ["USERPROFILE"], "AppData", "LocalLow", "Ankama", "Dofus", "RELEASE"
)

DOFUS_SHARED_PATH = os.path.join(RELEASE_FOLDER, "Shared", "dofus.json")
ACCOUNT_PATHS = os.path.join(RELEASE_FOLDER, "Accounts")


def set_config_key_values(path: str, config: dict[str, Any]):
    with open(path, "r+") as file:
        try:
            content: dict[str, Any] = json.load(file)
        except json.JSONDecodeError:
            return
    for key, value in config.items():
        content[key] = value
    with open(path, "w+") as file:
        json.dump(content, file)


if __name__ == "__main__":
    set_config_key_values(DOFUS_SHARED_PATH, low_consumption_config)
    for root, dirs, files in os.walk(ACCOUNT_PATHS):
        for file in files:
            if file == "dofus.json":
                set_config_key_values(os.path.join(root, file), low_consumption_config)
