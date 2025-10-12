import os

LineFilePath = str | os.PathLike[str]


def read_lines(path: LineFilePath, *, encoding: str | None = None) -> list[str]:
    with open(path, encoding=encoding) as handle:
        return handle.readlines()


def write_lines(
    path: LineFilePath,
    lines: list[str],
    *,
    create_parent: bool = False,
    encoding: str | None = None,
) -> None:
    if create_parent:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=encoding) as handle:
        handle.writelines(lines)
