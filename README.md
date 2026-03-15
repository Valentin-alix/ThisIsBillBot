# Bill

A Dofus Unity bot for Windows with a graphical interface for managing multiple
accounts, running harvesting, combat, or crafting activities, and scheduling them.

## What you can do

- **Control your accounts**: choose an activity and an area, then start or stop the bot from the interface.
- **Schedule sessions**: define several time slots per day and assign accounts to a schedule.
- **Prepare crafts**: search supported professions for recipes and add them to the crafting list.
- **Configure automation**: choose behaviors and manage email accounts and proxies in Settings.
- **Monitor operations**: review errors on the **Activity** page.

## What the project includes

The bot is written in Python and uses PyQt6 and FluentWidgets for its interface.
It supports two connection modes:

- **Socket**: communicates directly with the game servers without using the Dofus Unity client.
- **MITM**: sits between the Dofus Unity client and the servers to intercept and process their traffic.

In both modes, received messages update the game state, which harvesting, combat,
and crafting behaviors react to.

The repository also contains supporting tools:

- **An Ankama launcher emulator** for interactions with Ankama services.
- **A protocol mapper** that matches obfuscated messages and fields to their unobfuscated counterparts, primarily through static analysis with the IDA Pro API. See the [protobuf mapping guide](docs/mapping.md).
- **A Unity static-data reader** for game data such as items, recipes, spells, monsters, and maps.

## Getting started

### From source

Requirements: **Windows**, **Python 3.12**, **Git LFS**, and **uv**.
Clone this repository, then open PowerShell in its root directory:

```powershell
git lfs install
git lfs pull
uv sync
uv run playwright install chromium
Copy-Item .env.example .env
uv run python __main__.py
```

Copy `.env.example` only during the first installation; keep your existing `.env`
if you already have one.

MITM mode requires Dofus Unity installed through the Ankama launcher. Cytrus is
optional and is only used for automatic updates. The mapping tools are not
required to open the interface.

### Initial configuration

1. Under **Settings → Behaviors**, choose the activities to automate.
2. Under **Settings → Schedules**, define operating days and times.
3. Under **Settings → Accounts**, assign accounts to the available profiles.
4. Use the account controls to start an activity; check **Activity** if an error occurs.

Behavior changes take effect the next time the bot starts. Account automation
settings take effect at the next operation without interrupting the current one.

See the [interface configuration guide](docs/configuration.md) for accounts,
schedules, email accounts, proxies, and services.

## Development

The bot code is in `src/`, the launcher is in `AnkamaLauncherEmulator/`, and the
data and mapping tools are in `DBDofusUnity/`.

Each new Dofus build obfuscates protobuf message and field names again. The
mapping must therefore be regenerated and verified before the protocol can be
considered up to date.

```powershell
uv run ruff check .
uv run pyright
uv run pytest tests
```

The final `uv run poe verify` check also applies Ruff fixes. See the
[architecture and development guide](docs/maintenance.md) to understand the code
organization and extend the bot.
