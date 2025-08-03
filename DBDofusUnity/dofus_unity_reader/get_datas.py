import subprocess
import tempfile
from collections.abc import Iterable
from pathlib import Path

from tqdm import tqdm

from consts import (
    BUNDLES_ROOT,
    DATA_BUNDLES_ROOT,
    I18N_OUTPUT_PATH,
    I18N_PATH,
    MAP_BUNDLES_ROOT,
    PATH_DATAS,
    PATH_MAPS,
    PATH_STANDALONE_BUNDLES,
    STANDALONE_BUNDLES_ROOT,
    UABEA_PATH_EXE,
)
from dofus_unity_reader.extraction_manifest import ExtractionManifest
from dofus_unity_reader.generator.data_cleaning import clean_data_to_output
from dofus_unity_reader.generator.i18n import I18NReader
from dofus_unity_reader.models.maps import MapDataRoot
from dofus_unity_reader.models.world_graph import WorldGraphData

type DataModel = type[object]

MANIFEST_PATH = BUNDLES_ROOT / ".extraction_manifest.json"


def _run_uabea_batch_export(bundle_path: str, output_dir: str) -> None:
    subprocess.run(
        [str(UABEA_PATH_EXE), "batchexportbundle", bundle_path, "-out", output_dir],
        check=True,
    )


def _ensure_output_dirs() -> None:
    DATA_BUNDLES_ROOT.mkdir(parents=True, exist_ok=True)
    MAP_BUNDLES_ROOT.mkdir(parents=True, exist_ok=True)
    STANDALONE_BUNDLES_ROOT.mkdir(parents=True, exist_ok=True)


def _json_file_state(output_dir: Path) -> dict[str, int]:
    if not output_dir.exists():
        return {}
    return {
        path.name: path.stat().st_mtime_ns
        for path in output_dir.iterdir()
        if path.is_file() and path.suffix == ".json"
    }


def _changed_json_outputs(output_dir: Path, before_state: dict[str, int]) -> list[Path]:
    outputs: list[Path] = []
    for path in output_dir.iterdir():
        if not path.is_file() or path.suffix != ".json":
            continue
        if before_state.get(path.name) != path.stat().st_mtime_ns:
            outputs.append(path)
    return outputs


def _iter_json_files(output_dir: Path) -> Iterable[Path]:
    if not output_dir.exists():
        return ()
    return (path for path in output_dir.iterdir() if path.is_file() and path.suffix == ".json")


def _clean_stale_outputs(manifest: ExtractionManifest, output_dirs: Iterable[Path]) -> None:
    referenced_outputs = {path.resolve() for path in manifest.referenced_outputs()}
    for output_dir in output_dirs:
        for path in _iter_json_files(output_dir):
            if path.resolve() not in referenced_outputs:
                path.unlink()


def _move_cleaned_map_exports(temp_output_dir: Path) -> list[Path]:
    output_paths: list[Path] = []
    for exported_path in sorted(temp_output_dir.iterdir()):
        if not exported_path.is_file() or exported_path.suffix != ".json":
            continue

        clean_data_to_output(MapDataRoot, exported_path)
        output_path = MAP_BUNDLES_ROOT / exported_path.name
        exported_path.replace(output_path)
        output_paths.append(output_path)
    return output_paths


def get_world_graph_datas(*, manifest: ExtractionManifest) -> None:
    print("get world graph")
    bundle_filename = next(
        path.name for path in PATH_STANDALONE_BUNDLES.iterdir() if "worldassets_assets_all" in path.name
    )
    bundle_path = PATH_STANDALONE_BUNDLES / bundle_filename
    output_path = STANDALONE_BUNDLES_ROOT / WorldGraphData.FILE_PATH
    if manifest.is_up_to_date(bundle_path, output_paths=[output_path]):
        print("world graph is up to date")
        return

    before_state = _json_file_state(STANDALONE_BUNDLES_ROOT)
    _run_uabea_batch_export(
        bundle_path=str(bundle_path),
        output_dir=str(STANDALONE_BUNDLES_ROOT),
    )

    print("cleaning worldgraph")
    for path in STANDALONE_BUNDLES_ROOT.iterdir():
        if path.name == "world-graph.json":
            clean_data_to_output(WorldGraphData, path)
            continue
        path.unlink()
    outputs = _changed_json_outputs(STANDALONE_BUNDLES_ROOT, before_state)
    manifest.mark_success(bundle_path, output_paths=outputs or [output_path])
    manifest.save()


def get_map_datas(*, manifest: ExtractionManifest) -> None:
    print("get maps")

    map_bundles = sorted(
        path
        for path in PATH_MAPS.iterdir()
        if "mapdata_assets_world" in path.name and path.name.endswith(".bundle")
    )
    for bundle_path in tqdm(map_bundles):
        if manifest.is_up_to_date(bundle_path):
            continue

        with tempfile.TemporaryDirectory(prefix=f"{bundle_path.stem}-", dir=MAP_BUNDLES_ROOT) as temp_dir:
            temp_output_dir = Path(temp_dir)
            _run_uabea_batch_export(bundle_path=str(bundle_path), output_dir=str(temp_output_dir))
            outputs = _move_cleaned_map_exports(temp_output_dir)
        manifest.mark_success(bundle_path, output_paths=outputs)
        manifest.save()


def get_datas(*, manifest: ExtractionManifest) -> None:
    print("get content data")
    for path in tqdm(sorted(PATH_DATAS.iterdir())):
        if not path.is_file():
            continue
        if manifest.is_up_to_date(path):
            continue
        before_state = _json_file_state(DATA_BUNDLES_ROOT)
        _run_uabea_batch_export(bundle_path=str(path), output_dir=str(DATA_BUNDLES_ROOT))
        manifest.mark_success(path, output_paths=_changed_json_outputs(DATA_BUNDLES_ROOT, before_state))
        manifest.save()


def get_i18n_datas(*, manifest: ExtractionManifest) -> None:
    print("get i18n")
    source_path = Path(I18N_PATH)
    if manifest.is_up_to_date(source_path, output_paths=[I18N_OUTPUT_PATH]):
        print("i18n is up to date")
        return
    I18NReader.get_datas()
    manifest.mark_success(source_path, output_paths=[I18N_OUTPUT_PATH])
    manifest.save()


def update_all_datas() -> None:
    _ensure_output_dirs()
    manifest = ExtractionManifest.load(MANIFEST_PATH)
    get_datas(manifest=manifest)
    get_world_graph_datas(manifest=manifest)
    get_i18n_datas(manifest=manifest)
    get_map_datas(manifest=manifest)
    manifest.save()

    _clean_stale_outputs(manifest, [DATA_BUNDLES_ROOT, MAP_BUNDLES_ROOT, STANDALONE_BUNDLES_ROOT])
