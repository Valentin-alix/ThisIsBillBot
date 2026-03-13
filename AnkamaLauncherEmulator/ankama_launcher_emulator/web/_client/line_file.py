import os

LineFilePath = str | os.PathLike[str]


def read_lines(path: LineFilePath, *, encoding: str | None = None) -> list[str]:
    with open(path, encoding=encoding) as handle:
        return handle.readlines()
