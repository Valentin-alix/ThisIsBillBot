# Ankama Launcher Emulator

A tool that emulates the Ankama Launcher to launch **Dofus 3** and **Dofus RETRO** directly — without needing the official launcher running. Supports multi-account management, per-account SOCKS5 proxies, and network interface selection, all from a Qt desktop application.

![alt text](docs/screenshot.png)

## How to use it

Simply get the `.exe` in Releases and execute it.

> **Note:** Install `cytrus-v6` to enable automatic game updates before each launch:
> ```bash
> npm install -g cytrus-v6
> ```
> Without it, the tool still works but won't auto-update your game files.

Then you access this beautiful (no) interface

---

## How it works

The official Ankama Launcher stores your credentials encrypted in `%APPDATA%\zaap\`. This tool:

1. Reads and decrypts those stored API keys using your machine's UUID
2. Starts a local Thrift server on port `26116` (the same port the game expects from the launcher)
3. Intercepts the game's connection via a transparent proxy (mitmproxy)
4. Optionally checks for game updates via `cytrus-v6` before launching
5. Launches `Dofus.exe` with the correct arguments so it connects to the local emulated launcher instead of Zaap

You must have logged in at least once through the official Ankama Launcher so that your credentials are stored locally.

---

## Requirements

- **Dofus 3** or **RETRO** installed via the official Ankama Launcher (at least one account logged in)
- **Python >= 3.12**
- **uv** — fast Python package manager
- **cytrus-v6** *(optional)* — enables automatic game updates at launch time

Install uv:

```bash
pip install uv
```

Install cytrus-v6 (optional but recommended):

```bash
npm install -g cytrus-v6
```

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Valentin-alix/AnkamaLauncherEmulator
cd AnkamaLauncherEmulator
uv sync
```

---

## Usage

### Run from source

```bash
uv run main.py
```

### Run the packaged executable

Download the latest release or build it yourself (see [Packaging](#packaging)), then simply run `main.exe`.

### Using the UI

Select the game (Dofus 3 or Dofus Retro) using the cards at the top. Each stored account appears below as a card. For each account you can:

| Option              | Description                                                                |
| ------------------- | -------------------------------------------------------------------------- |
| **Local interface** | Select which network interface Dofus will use (useful for multi-IP setups) |
| **Proxy URL**       | Optional SOCKS5 proxy for this account (`socks5://user:pass@host:port`)    |
| **Launch**          | Start a Dofus 3 or Retro instance for this account                         |

If `cytrus-v6` is installed, a download banner will appear with progress before the game starts while it checks/downloads updates.

Accounts and network interfaces are refreshed automatically every 10 seconds.

> **Note:** You can launch multiple accounts simultaneously, each with its own proxy and interface.

---

## Packaging

Build a standalone `.exe` with PyInstaller:

```bash
uv run pyinstaller main.spec
```

The output will be in the `dist/` folder.

---

## Development

### Install dev dependencies

```bash
uv sync --group dev
```

### Regenerate Thrift bindings

If `resources/zaap.thrift` changes, regenerate the Python bindings:

```bash
thrift --gen py resources/zaap.thrift && mv gen-py ankama_launcher_emulator/gen_zaap
```

### Inspect the Ankama Launcher source

To explore the launcher's internals, extract the `app.asar` bundle:

```bash
asar extract "C:/Program Files/Ankama/Ankama Launcher/resources/app.asar" "<output_dir>"
```

---

## Use as a library

Add the package to your own project:

```bash
pip install git+https://github.com/Valentin-alix/AnkamaLauncherEmulator
```
