# Architecture and development

[Back to the README](../README.md)

## From messages to actions

Socket and MITM connections feed the same message-processing pipeline. After
decoding, `EventManager` sends messages to frames, which update `GameState`, the
representation of the current game state. Behaviors use that state to decide
which actions to perform.

The PyQt6 and FluentWidgets interface controls accounts, selects their activities,
and schedules sessions.

## Repository structure

- **`src/`**: graphical interface, network connections, game state, and automated behaviors.
- **`AnkamaLauncherEmulator/`**: interactions with Ankama services, including login and account-management flows.
- **`DBDofusUnity/`**: tools for reading Unity static data and matching the obfuscated protocol to unobfuscated definitions.

The mapper primarily uses static analysis with IDA Pro to identify message and
field mappings. Runtime traffic observations supplement this analysis. The data
reader exposes game information used by behaviors, such as maps, items, recipes,
and spells.

## Extending the bot

- Add a `Behavior` for a high-level operation.
- Add a `Frame` to update `GameState` from game messages.
- Adapt email providers, socket/MITM modes, and mapping tools.
- Configure profiles, proxies, and accounts through the interface or local JSON files, never in code or examples.

Before working on the protocol, read the
[mapper instructions](../DBDofusUnity/proto_mapper_assembly/AGENTS.md).
