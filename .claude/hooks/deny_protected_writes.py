"""PreToolUse hook (Bash): block shell commands that look like they modify protected data files."""

import json
import re
import sys

PROTECTED_PATH_PATTERNS = [
    r"mail_accounts\.json",
    r"paysafecards\.txt",
    r"(^|/)bots\.json",
    r"(^|/)bots\.local\.json",
    r"proxies\.json",
    r"DBDofusUnity/datas/bundles",
    r"DBDofusUnity/datas/protos/non_obf",
    r"DBDofusUnity/datas/protos/obf",
    r"DBDofusUnity/datas/proto_mapper/non_obf",
    r"DBDofusUnity/datas/proto_mapper/obf",
    r"instancied_msg_infos\.json",
    r"unknown_name_registry\.json",
    r"game_mappings\.json",
    r"game_mappings_detailed\.json",
]

MUTATING_PATTERNS = [
    r"(^|[;&|]|\s)rm\s",
    r"(^|[;&|]|\s)mv\s",
    r"(^|[;&|]|\s)cp\s",
    r"sed\s+-i",
    r"perl\s+-i",
    r">>?(?!&)",
    r"\btee\b",
    r"truncate\s",
    r"dd\s+of=",
    r"git\s+checkout\s+--",
    r"git\s+reset\s+--hard",
    r"git\s+clean\s",
    r"\.write\(",
    r"Out-File|Set-Content|Add-Content|Remove-Item|Move-Item|Copy-Item",
]


def main() -> None:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return

    touches_protected = any(re.search(p, command, re.IGNORECASE) for p in PROTECTED_PATH_PATTERNS)
    if not touches_protected:
        return

    looks_mutating = any(re.search(p, command, re.IGNORECASE) for p in MUTATING_PATTERNS)
    if not looks_mutating:
        return

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "Blocked: this command appears to modify a protected data file "
                        "(mail_accounts.json, paysafecards.txt, bots(.local).json, proxies.json, "
                        "or protocol data under DBDofusUnity/datas). Edit it manually if truly needed."
                    ),
                }
            }
        )
    )


if __name__ == "__main__":
    main()
