from __future__ import annotations

from pathlib import Path

PROTO_CS_CODE: str = """
public sealed class itl : IMessage<itl>, IBufferMessage // TypeDefIndex: 1
{
    private UnknownFieldSet dtti; // 0x10
    private int fhft_; // 0x18
    private bool fhfu_; // 0x1C
}
"""

CORE_CS_CODE: str = """
public class Owner // TypeDefIndex: 2
{
    public Holder holder; // 0x10
}

public class Holder // TypeDefIndex: 3
{
    public itl request; // 0x20
}
"""


def write_proto_cs_files(tmp_path: Path, *, include_core: bool) -> tuple[Path, Path]:
    cs_dir = tmp_path / "cs"
    cs_dir.mkdir()

    proto_path = cs_dir / "Ankama.Dofus.Protocol.Game.cs"
    proto_path.write_text(PROTO_CS_CODE, encoding="utf-8")

    if include_core:
        (cs_dir / "Core.cs").write_text(CORE_CS_CODE, encoding="utf-8")

    return tmp_path, proto_path


def write_custom_cs_files(
    tmp_path: Path,
    *,
    proto_code: str,
    core_code: str,
) -> tuple[Path, Path]:
    cs_dir = tmp_path / "cs"
    cs_dir.mkdir()

    proto_path = cs_dir / "Ankama.Dofus.Protocol.Game.cs"
    proto_path.write_text(proto_code, encoding="utf-8")
    (cs_dir / "Core.cs").write_text(core_code, encoding="utf-8")

    return tmp_path, proto_path
