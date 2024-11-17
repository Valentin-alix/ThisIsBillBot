# Ankama Launcher Emulator

## Requirements

- python >= 3.12
- uv (https://github.com/astral-sh/uv)
    `pip install uv`
- Install dependencies
    `uv sync`

## Running an Account

Go to `src/server/server.py`, modify the login, then run:
```bash
python src/server/server.py
```

## Code Generation

To generate code from `zaap.thrift`:
```bash
thrift --gen py resources/zaap.thrift && mv gen-py src/gen_zaap
```

## Installation

Install the package:
```bash
poetry add git+https://github.com/Valentin-alix/AnkamaLauncherEmulator
```

## Debugging

Extract the `app.asar` file:
```bash
asar extract "C://Program Files//Ankama//Ankama Launcher//resources//app.asar" "D:/Ankama Games/AnkamaLauncher/AnkaLauncherExtracted"
```
