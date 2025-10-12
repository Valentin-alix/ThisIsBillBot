"""
Recover the mappings an archived build was actually shipped with, out of git history.

The metric audit needs one ``game_mappings.json`` per archived build, and re-running the mapper to
produce it would be circular: the mapper would be graded against its own output. The committed
mappings are the honest reference instead, having been corrected by hand over the days each build
was live.

Which commit belongs to which build is not recorded, but it is derivable. A build is live from the
moment its ``GameAssembly.dll`` was archived until the next build replaces it, so the mappings it
shipped with are the last ones committed inside that window.

That window is then checked rather than trusted. Obfuscated *class* names are useless for this:
they are three letters drawn from a small alphabet, and more than half of them survive from one
build to the next, so a mappings file from any era resolves against any dump. Obfuscated *field*
names are the discriminating signal, because a candidate only scores if each obfuscated class it
names also contains every obfuscated field it binds. A wrong build fails that joint constraint.

Nothing is written without ``--write``.
"""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from DBDofusUnity.consts import OBF_GAME_SNAPSHOTS_DIR, PROJECT_ROOT

from DBDofusUnity.proto_mapper_assembly.controllers.message_lookup import build_obf_alias_lookup
from DBDofusUnity.proto_mapper_assembly.helpers.archived_builds import (
    GAME_MAPPINGS_RELATIVE_PATH,
    PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
    game_assembly_mtime_ns,
    iter_archived_build_dirs,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import SimpleGameMappingsDocument
from DBDofusUnity.proto_mapper_assembly.parsers.dump_cs_parser import parse_messages

_GAME_MAPPINGS_REPO_PATH = "datas/protos/game_mappings.json"
_CONFIDENT_FIELD_RATIO = 0.90


@dataclass(frozen=True)
class CommitCandidate:
    commit: str
    committed_at: str
    subject: str
    mapping_count: int
    checked_field_count: int
    matched_field_count: int

    @property
    def field_ratio(self) -> float:
        if self.checked_field_count == 0:
            return 0.0
        return self.matched_field_count / self.checked_field_count


def main() -> None:
    arguments = _build_argument_parser().parse_args()
    obf_dir: Path = arguments.obf_dir
    dump_cs_path = obf_dir / PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH
    if not dump_cs_path.is_file():
        error_message = f"{dump_cs_path} not found; dump this build before recovering its mappings"
        raise SystemExit(error_message)

    obf_messages_by_cls = {message.composed_name: message for message in parse_messages(str(dump_cs_path))}
    obf_alias_to_cls = build_obf_alias_lookup(obf_messages_by_cls=obf_messages_by_cls)
    # ``field_mapping`` is keyed by the obfuscated *property* name, the ``fnaw`` of
    # ``public jyw fnaw { get; set; }``, so the backing field name would never match.
    obf_field_names_by_cls = {
        message_cls: frozenset(
            field.property_name for field in message.fields if field.property_name is not None
        )
        for message_cls, message in obf_messages_by_cls.items()
    }

    window_start, window_end = resolve_build_window(obf_dir=obf_dir, snapshots_root=arguments.snapshots_root)
    print(f"build: {obf_dir.name}")
    print(f"live window: {window_start} .. {window_end or 'now'}\n")

    commits = iter_mapping_commits(window_start=window_start, window_end=window_end)
    if not commits:
        raise SystemExit("no mappings commit inside this build's live window")

    candidates = [
        _score_commit(
            commit=commit,
            committed_at=committed_at,
            subject=subject,
            obf_alias_to_cls=obf_alias_to_cls,
            obf_field_names_by_cls=obf_field_names_by_cls,
        )
        for commit, committed_at, subject in commits
    ]

    print("| commit | date | mappings | fields ok | ratio | subject |")
    print("|---|---|---:|---:|---:|---|")
    for candidate in candidates[: arguments.top]:
        print(
            f"| {candidate.commit[:8]} "
            f"| {candidate.committed_at} "
            f"| {candidate.mapping_count} "
            f"| {candidate.matched_field_count}/{candidate.checked_field_count} "
            f"| {candidate.field_ratio:.4f} "
            f"| {candidate.subject} |"
        )

    # Newest inside the window: the state the build was left in when it was replaced.
    best = candidates[0]
    if best.field_ratio < _CONFIDENT_FIELD_RATIO:
        print(
            f"\n{best.commit[:8]} binds only {best.field_ratio:.4f} of its obfuscated fields to "
            f"classes of this build. The window is probably wrong, or this build predates the "
            "history. Not writing anything."
        )
        raise SystemExit(1)

    print(f"\nselected: {best.commit[:8]} ({best.committed_at}) {best.subject}")
    if not arguments.write:
        print("re-run with --write to store it next to the build")
        return

    output_path = obf_dir / GAME_MAPPINGS_RELATIVE_PATH
    output_path.write_bytes(_read_mappings_at_commit(best.commit))
    print(f"written: {output_path}")


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obf-dir", type=Path, required=True, help="Archived build directory.")
    parser.add_argument(
        "--snapshots-root",
        type=Path,
        default=OBF_GAME_SNAPSHOTS_DIR,
        help="Directory holding one sub-directory per archived build, used to bound the live window.",
    )
    parser.add_argument("--top", type=int, default=10, help="How many candidates to print.")
    parser.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="Store the winning mappings as game_mappings.json inside the build directory.",
    )
    return parser


def resolve_build_window(*, obf_dir: Path, snapshots_root: Path) -> tuple[str, str | None]:
    """Return the git date bounds during which this build was the one installed."""
    build_times = sorted(
        game_assembly_mtime_ns(version_dir)
        for version_dir in iter_archived_build_dirs(snapshots_root=snapshots_root)
    )
    own_time = game_assembly_mtime_ns(obf_dir)
    later_times = [build_time for build_time in build_times if build_time > own_time]
    return _format_git_date(own_time), _format_git_date(min(later_times)) if later_times else None


def _format_git_date(mtime_ns: int) -> str:
    return datetime.fromtimestamp(mtime_ns / 1_000_000_000).astimezone().strftime("%Y-%m-%d %H:%M:%S")


def iter_mapping_commits(*, window_start: str, window_end: str | None) -> list[tuple[str, str, str]]:
    arguments = ["log", f"--since={window_start}", "--format=%H%x00%cd%x00%s", "--date=format:%Y-%m-%d %H:%M"]
    if window_end is not None:
        arguments.append(f"--until={window_end}")
    output = _run_git(*arguments, "--", _GAME_MAPPINGS_REPO_PATH)
    commits: list[tuple[str, str, str]] = []
    for line in output.decode("utf-8", errors="replace").splitlines():
        parts = line.split("\x00")
        if len(parts) == 3:
            commits.append((parts[0], parts[1], parts[2]))
    return commits


def _read_mappings_at_commit(commit: str) -> bytes:
    return _run_git("show", f"{commit}:{_GAME_MAPPINGS_REPO_PATH}")


def _score_commit(
    *,
    commit: str,
    committed_at: str,
    subject: str,
    obf_alias_to_cls: dict[str, frozenset[str]],
    obf_field_names_by_cls: dict[str, frozenset[str]],
) -> CommitCandidate:
    mappings = SimpleGameMappingsDocument.model_validate_json(_read_mappings_at_commit(commit)).root
    checked_field_count = 0
    matched_field_count = 0
    empty_field_names: frozenset[str] = frozenset()
    for entry in mappings.values():
        candidates = obf_alias_to_cls.get(entry.obf_msg_namespace, frozenset())
        obf_field_names = (
            obf_field_names_by_cls.get(next(iter(candidates)), empty_field_names)
            if len(candidates) == 1
            else empty_field_names
        )
        for obf_field_name in entry.field_mapping:
            checked_field_count += 1
            matched_field_count += obf_field_name in obf_field_names
    return CommitCandidate(
        commit=commit,
        committed_at=committed_at,
        subject=subject,
        mapping_count=len(mappings),
        checked_field_count=checked_field_count,
        matched_field_count=matched_field_count,
    )


def _run_git(*arguments: str) -> bytes:
    return subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


if __name__ == "__main__":
    main()
