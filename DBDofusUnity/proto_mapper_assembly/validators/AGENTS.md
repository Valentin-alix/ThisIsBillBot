# Validators

- Let unexpected exceptions propagate to the caller. Catch conversion errors only when they mean the input is invalid and return `False`.
- Fields in `global_validators` and `set_validators` must not be nested: nested messages are not remapped.
- In `field_validators.py`, key `VALIDATORS_ON_FIELD` by generated protobuf classes (`type[Message]`); group entries by source module under a `# <module>_pb2` comment. Keep field names as strings checked against descriptors at import time.
