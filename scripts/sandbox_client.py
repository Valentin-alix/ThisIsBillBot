import argparse
import socket
import sys

END_SENTINEL = "---END---"


def _read_code(args: argparse.Namespace) -> str:
    if args.file is not None:
        with open(args.file, encoding="utf-8") as file:
            return file.read()
    if args.code is not None:
        return str(args.code)
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6666)
    parser.add_argument("--login", help="Bot login to run code against")
    parser.add_argument("--code", help="Inline Python code to run")
    parser.add_argument("--file", help="Path to a Python file to run")
    parser.add_argument("--list", action="store_true", help="List connected bot logins")
    args = parser.parse_args()

    if not args.list and not args.login:
        parser.error("--login is required unless --list is given")

    with socket.create_connection((args.host, args.port)) as connection:
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
        print(response.decode(errors="replace"), end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
