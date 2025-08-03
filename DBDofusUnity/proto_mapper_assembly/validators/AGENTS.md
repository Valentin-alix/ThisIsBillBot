## Rules

DONT catch exception in validators function, except if it's for lisibility, because it's the caller who must catch exceptions.

fields in global_validators and set_validators CAN'T BE nested, because the nested message is not remapped

### field_validators.py
Keys of VALIDATORS_ON_FIELD are `type[Message]` (the generated protobuf class imported from `datas.protos.non_obf.game.*_pb2`). Entries MUST be grouped by their source pb2 module, with a `# <module>_pb2` comment on top of each group. Field names stay as `str` and are checked at module import time against `cls.DESCRIPTOR.fields_by_name`.