import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from DBDofusUnity.proto_mapper_assembly.scripts.audit_historical_assembly_metrics import (
    MetricSample,
    MetricSummary,
    NonObfReference,
    VersionSource,
    _build_recommendations,
    _collect_version_heads,
    _iter_version_dirs,
    _summarize_samples,
)

_GAME_ASSEMBLY_NAME = "GameAssembly.dll"
_EMPTY_TRACE = '{"functions_by_address": {}}'

_NON_OBF_PROTO_ACCESSES_PATH = Path("non_obf") / "proto_accesses.json"
_NON_OBF_DUMP_CS_PATH = Path("non_obf") / "cs" / "Ankama.Dofus.Protocol.Game.cs"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_fallback_reference(root: Path) -> NonObfReference:
    fallback_dir = root / "fallback_non_obf"
    proto_accesses_path = fallback_dir / "proto_accesses.json"
    dump_cs_path = fallback_dir / "cs" / "Ankama.Dofus.Protocol.Game.cs"
    _write(proto_accesses_path, _EMPTY_TRACE)
    _write(dump_cs_path, "// fallback non obf dump\n")
    return NonObfReference(proto_accesses_path=proto_accesses_path, dump_cs_path=dump_cs_path)


def _build_version_dir(
    root: Path,
    version_id: str,
    *,
    game_assembly_mtime_ns: int,
    obf_dump: str = "// obf dump\n",
    mappings: str = "{}",
    skip_paths: tuple[Path, ...] = (),
    skip_non_obf: bool = False,
) -> Path:
    version_dir = root / version_id
    version_dir.mkdir(parents=True, exist_ok=True)
    game_assembly = version_dir / _GAME_ASSEMBLY_NAME
    game_assembly.write_bytes(b"MZ")
    os.utime(game_assembly, ns=(game_assembly_mtime_ns, game_assembly_mtime_ns))

    contents_by_path = {
        Path("proto_accesses.json"): _EMPTY_TRACE,
        _NON_OBF_PROTO_ACCESSES_PATH: _EMPTY_TRACE,
        Path("cs") / "Ankama.Dofus.Protocol.Game.cs": obf_dump,
        _NON_OBF_DUMP_CS_PATH: "// non obf dump\n",
        Path("game_mappings.json"): mappings,
    }
    skipped = set(skip_paths)
    if skip_non_obf:
        skipped |= {_NON_OBF_PROTO_ACCESSES_PATH, _NON_OBF_DUMP_CS_PATH}
    for relative_path, content in contents_by_path.items():
        if relative_path in skipped:
            continue
        _write(version_dir / relative_path, content)
    return version_dir


class TestVersionDirDiscovery(unittest.TestCase):
    def test_lists_build_dirs_newest_first_and_excludes_the_non_obf_reference(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            _build_version_dir(root, "old_build", game_assembly_mtime_ns=1_000_000_000)
            _build_version_dir(root, "new_build", game_assembly_mtime_ns=3_000_000_000)
            non_obf_dir = _build_version_dir(root, "BETA", game_assembly_mtime_ns=2_000_000_000)
            (root / "not_a_build").mkdir()

            version_dirs = _iter_version_dirs(snapshots_root=root, non_obf_game_dir=non_obf_dir)

            self.assertEqual([path.name for path in version_dirs], ["new_build", "old_build"])

    def test_missing_snapshots_root_yields_no_version(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name) / "absent"

            version_dirs = _iter_version_dirs(snapshots_root=root, non_obf_game_dir=root / "BETA")

            self.assertEqual(version_dirs, [])


class TestCollectVersionHeads(unittest.TestCase):
    def test_incomplete_build_is_skipped_and_reports_its_missing_artifacts(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            _build_version_dir(root, "complete", game_assembly_mtime_ns=2_000_000_000)
            _build_version_dir(
                root,
                "incomplete",
                game_assembly_mtime_ns=1_000_000_000,
                skip_paths=(Path("game_mappings.json"),),
            )

            result = _collect_version_heads(
                snapshots_root=root,
                non_obf_game_dir=root / "BETA",
                non_obf_fallback=_build_fallback_reference(root),
            )

            self.assertEqual([head.version_id for head in result.version_heads], ["complete"])
            self.assertEqual([version.version_id for version in result.incomplete_versions], ["incomplete"])
            self.assertEqual(result.incomplete_versions[0].missing_paths, (Path("game_mappings.json"),))

    def test_build_without_an_archived_reference_falls_back_to_the_live_one(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            fallback = _build_fallback_reference(root)
            _build_version_dir(root, "archived", game_assembly_mtime_ns=2_000_000_000)
            _build_version_dir(
                root,
                "obf_only",
                game_assembly_mtime_ns=1_000_000_000,
                obf_dump="// other obf dump\n",
                skip_non_obf=True,
            )

            result = _collect_version_heads(
                snapshots_root=root,
                non_obf_game_dir=root / "BETA",
                non_obf_fallback=fallback,
            )

            self.assertEqual(result.incomplete_versions, [])
            head_by_id = {head.version_id: head for head in result.version_heads}
            self.assertEqual(head_by_id["archived"].non_obf_source, "snapshot")
            self.assertEqual(head_by_id["obf_only"].non_obf_source, "fallback")
            self.assertEqual(head_by_id["obf_only"].non_obf_dump_cs_path, fallback.dump_cs_path)

    def test_forcing_the_fallback_ignores_an_archived_reference(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            fallback = _build_fallback_reference(root)
            _build_version_dir(root, "archived", game_assembly_mtime_ns=1_000_000_000)

            result = _collect_version_heads(
                snapshots_root=root,
                non_obf_game_dir=root / "BETA",
                non_obf_fallback=fallback,
                force_non_obf_fallback=True,
            )

            head = result.version_heads[0]
            self.assertEqual(head.non_obf_source, "fallback")
            self.assertEqual(head.non_obf_proto_accesses_path, fallback.proto_accesses_path)

    def test_build_is_incomplete_when_neither_archived_nor_fallback_reference_exists(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            _build_version_dir(root, "obf_only", game_assembly_mtime_ns=1_000_000_000, skip_non_obf=True)
            absent = root / "absent"

            result = _collect_version_heads(
                snapshots_root=root,
                non_obf_game_dir=root / "BETA",
                non_obf_fallback=NonObfReference(
                    proto_accesses_path=absent / "proto_accesses.json",
                    dump_cs_path=absent / "dump.cs",
                ),
            )

            self.assertEqual(result.version_heads, [])
            self.assertEqual([version.version_id for version in result.incomplete_versions], ["obf_only"])

    def test_extra_source_is_audited_first_and_wins_the_dedup_against_its_own_snapshot(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            fallback = _build_fallback_reference(root)
            _build_version_dir(root, "archived", game_assembly_mtime_ns=1_000_000_000)
            already_archived = _build_version_dir(
                root,
                "same_as_working_set",
                game_assembly_mtime_ns=2_000_000_000,
                obf_dump="// live obf dump\n",
            )
            live_dir = _build_version_dir(
                root / "live", "obf", game_assembly_mtime_ns=5_000_000_000, obf_dump="// live obf dump\n"
            )

            result = _collect_version_heads(
                snapshots_root=root,
                non_obf_game_dir=root / "BETA",
                non_obf_fallback=fallback,
                extra_sources=(
                    VersionSource(
                        version_id="working_set",
                        obf_proto_accesses_path=live_dir / "proto_accesses.json",
                        obf_dump_cs_path=live_dir / "cs" / "Ankama.Dofus.Protocol.Game.cs",
                        game_mappings_path=live_dir / "game_mappings.json",
                        non_obf=fallback,
                    ),
                ),
            )

            self.assertEqual([head.version_id for head in result.version_heads], ["working_set", "archived"])
            self.assertNotIn(already_archived.name, [head.version_id for head in result.version_heads])

    def test_a_source_sharing_the_obf_dump_of_an_earlier_one_is_counted_once(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            _build_version_dir(root, "newer", game_assembly_mtime_ns=2_000_000_000, obf_dump="// same\n")
            _build_version_dir(root, "older", game_assembly_mtime_ns=1_000_000_000, obf_dump="// same\n")

            result = _collect_version_heads(
                snapshots_root=root,
                non_obf_game_dir=root / "BETA",
                non_obf_fallback=_build_fallback_reference(root),
            )

            self.assertEqual([head.version_id for head in result.version_heads], ["newer"])
            self.assertEqual(result.incomplete_versions, [])

    def test_head_carries_the_mapped_message_count_of_its_own_build(self) -> None:
        with TemporaryDirectory() as temporary_dir_name:
            root = Path(temporary_dir_name)
            _build_version_dir(
                root,
                "build",
                game_assembly_mtime_ns=1_000_000_000,
                mappings=(
                    '{".a.A": {"obf_msg_namespace": "aa", "field_mapping": {}}, '
                    '".a.B": {"obf_msg_namespace": "bb", "field_mapping": {}}}'
                ),
            )

            result = _collect_version_heads(
                snapshots_root=root,
                non_obf_game_dir=root / "BETA",
                non_obf_fallback=_build_fallback_reference(root),
            )

            self.assertEqual(result.version_heads[0].mapped_message_count, 2)


class TestSummarizeSamples(unittest.TestCase):
    def test_summarizes_stability_scores_and_discriminative_margins(self) -> None:
        stability_samples = [
            MetricSample(metric_name="metric_a", score=score) for score in (0.2, 0.4, 0.6, 0.8)
        ]
        discriminative_samples = [
            MetricSample(
                metric_name="metric_a",
                score=0.0,
                true_score=0.9,
                best_false_score=0.4,
                true_rank=1,
                candidate_count=5,
            ),
            MetricSample(
                metric_name="metric_a",
                score=0.0,
                true_score=0.5,
                best_false_score=0.6,
                true_rank=3,
                candidate_count=5,
            ),
        ]

        summaries = _summarize_samples(stability_samples, discriminative_samples)

        self.assertEqual(len(summaries), 1)
        summary = summaries[0]
        self.assertEqual(summary.sample_count, 4)
        self.assertAlmostEqual(summary.mean_score, 0.5)
        self.assertAlmostEqual(summary.p50_score, 0.6)
        assert summary.mean_margin is not None
        self.assertAlmostEqual(summary.mean_margin, 0.2)
        assert summary.top1_accuracy is not None
        self.assertAlmostEqual(summary.top1_accuracy, 0.5)
        assert summary.mean_rank is not None
        self.assertAlmostEqual(summary.mean_rank, 2.0)
        assert summary.collision_ratio is not None
        self.assertAlmostEqual(summary.collision_ratio, 0.5)

    def test_metric_without_discriminative_samples_leaves_margins_unset(self) -> None:
        summaries = _summarize_samples([MetricSample(metric_name="metric_a", score=1.0)], [])

        self.assertIsNone(summaries[0].mean_margin)
        self.assertIsNone(summaries[0].top1_accuracy)
        self.assertIsNone(summaries[0].collision_ratio)


def _summary(
    *,
    metric_name: str = "metric_a",
    mean_score: float = 0.9,
    p10_score: float = 0.9,
    mean_margin: float | None = 0.5,
    top1_accuracy: float | None = 0.9,
    collision_ratio: float | None = 0.0,
) -> MetricSummary:
    return MetricSummary(
        metric_name=metric_name,
        sample_count=10,
        coverage_ratio=1.0,
        mean_score=mean_score,
        p10_score=p10_score,
        p50_score=mean_score,
        p90_score=mean_score,
        mean_margin=mean_margin,
        top1_accuracy=top1_accuracy,
        mean_rank=1.0,
        collision_ratio=collision_ratio,
    )


class TestBuildRecommendations(unittest.TestCase):
    def test_healthy_metric_is_not_reported(self) -> None:
        self.assertEqual(_build_recommendations([_summary()]), [])

    def test_negative_margin_is_reported_as_an_anti_signal_however_stable(self) -> None:
        summaries = [_summary(mean_score=0.95, p10_score=0.95, mean_margin=-0.223, collision_ratio=0.72)]

        self.assertEqual(
            _build_recommendations(summaries),
            [
                "remove metric_a: anti-signal, the best wrong candidate outscores the right one "
                "by 0.223 on average"
            ],
        )

    def test_metric_that_never_separates_anything_is_reported_as_near_constant(self) -> None:
        summaries = [_summary(mean_score=0.99, p10_score=1.0, mean_margin=0.003, collision_ratio=0.986)]

        self.assertEqual(
            _build_recommendations(summaries),
            ["remove metric_a: near-constant, it separates nothing on 98.6% of pairs"],
        )

    def test_unstable_and_weakly_discriminative_metric_is_flagged_for_removal(self) -> None:
        summaries = [_summary(mean_score=0.2, mean_margin=0.01)]

        self.assertEqual(
            _build_recommendations(summaries),
            ["lower/remove metric_a: unstable and weakly discriminative"],
        )

    def test_stable_metric_failing_every_discriminative_threshold_is_only_lowered(self) -> None:
        summaries = [_summary(mean_margin=0.01, top1_accuracy=0.1, collision_ratio=0.5)]

        self.assertEqual(
            _build_recommendations(summaries),
            ["lower metric_a: discriminative margin is weak"],
        )
