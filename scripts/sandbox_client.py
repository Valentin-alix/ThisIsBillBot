import argparse
import json
import os
import socket
import sys
from typing import Any

END_SENTINEL = "---END---"

_EPILOG = """\
Examples:
  python scripts/sandbox_client.py --list
  python scripts/sandbox_client.py --login <login> --code "list_behaviors()"
  python scripts/sandbox_client.py --login <login> --code "list_messages('Fight')"
  python scripts/sandbox_client.py --login <login> --code "describe_message('...')"
  python scripts/sandbox_client.py --login <login> --code "reload()"
  python scripts/sandbox_client.py --login <login> --file snippet.py
  python scripts/sandbox_client.py --login <login> --json --code "game_state.debug_snapshot()"
"""


def _read_code(args: argparse.Namespace) -> str:
    if args.file is not None:
        with open(args.file, encoding="utf-8") as file:
            return file.read()
    if args.code is not None:
        return str(args.code)
    return sys.stdin.read()


def _format_list(payload: dict[str, Any]) -> str:
    bots = payload["bots"]
    if not bots:
        return "No bot connected.\n"
    lines: list[str] = []
    for bot in bots:
        lines.append(
            f"{bot['login']} (account_id={bot['account_id']}) "
            f"connected={bot['connected']} in_fight={bot['in_fight']} "
            f"current_behavior={bot['current_behavior']}"
        )
    return "\n".join(lines) + "\n"


def _format_result(payload: dict[str, Any]) -> str:
    parts = [f"STDOUT:\n{payload['stdout']}"]
    if payload["result"] is not None:
        parts.append(f"RESULT:\n{payload['result']}")
    if payload["error"] is not None:
        parts.append(f"ERROR:\n{payload['error']}")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Python code against a live bot via the sandbox server.",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("SANDBOX_PORT", "6666")))
    parser.add_argument("--login", help="Bot login to run code against")
    parser.add_argument("--code", help="Inline Python code to run")
    parser.add_argument("--file", help="Path to a Python file to run")
    parser.add_argument("--list", action="store_true", help="List connected bots and their status")
    parser.add_argument("--json", action="store_true", help="Print the raw JSON response instead of formatted text")
    args = parser.parse_args()

    if not args.list and not args.login:
        parser.error("--login is required unless --list is given")

    try:
        connection = socket.create_connection((args.host, args.port))
    except OSError as error:
        print(
            f"Sandbox unreachable at {args.host}:{args.port} ({error}). "
            "Is the bot running with SANDBOX_ENABLED=1?",
            file=sys.stderr,
        )
        return 1

    with connection:
        if args.list:
            connection.sendall(b"list\n")
        else:
            code = _read_code(args)
            connection.sendall(f"{args.login}\n{code}\n{END_SENTINEL}\n".encode())

        response = b""
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            response += chunk

    payload = json.loads(response.decode(errors="replace"))
    if args.json:
        print(json.dumps(payload, indent=2))
    elif args.list:
        print(_format_list(payload), end="")
    else:
        print(_format_result(payload), end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
