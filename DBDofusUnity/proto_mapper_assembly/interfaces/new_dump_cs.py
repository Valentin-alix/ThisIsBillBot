from __future__ import annotations

from pydantic import RootModel

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage


class NewDumpCSFile(RootModel[dict[str, DumpCSMessage]]):
    root: dict[str, DumpCSMessage]
