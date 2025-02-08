import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from proto_mapper_assembly.interfaces.pinned_pairs import upsert_pinned_field_mapping


class TestPinnedFieldMapping(unittest.TestCase):
    def test_creates_pair_with_field_mapping(self) -> None:
        path = self._temp_path()

        upsert_pinned_field_mapping(path, "obf.Msg", "ClearMsg", "a", "field_a")

        self.assertEqual(
            self._read_json(path),
            {
                "pairs": [
                    {
                        "obf": "obf.Msg",
                        "non_obf": "ClearMsg",
                        "field_mapping_by_obf": {"a": "field_a"},
                    }
                ]
            },
        )

    def test_adds_field_to_existing_pair(self) -> None:
        path = self._temp_path()
        path.write_text(
            json.dumps(
                {
                    "pairs": [
                        {
                            "obf": "obf.Msg",
                            "non_obf": "ClearMsg",
                            "field_mapping_by_obf": {"a": "field_a"},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        upsert_pinned_field_mapping(path, "obf.Msg", "ClearMsg", "b", "field_b")

        pair = self._read_json(path)["pairs"][0]
        self.assertEqual(
            pair["field_mapping_by_obf"],
            {"a": "field_a", "b": "field_b"},
        )

    def test_replaces_existing_obf_field_mapping(self) -> None:
        path = self._temp_path()
        path.write_text(
            json.dumps(
                {
                    "pairs": [
                        {
                            "obf": "obf.Msg",
                            "non_obf": "ClearMsg",
                            "field_mapping_by_obf": {"a": "old_field"},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        upsert_pinned_field_mapping(path, "obf.Msg", "ClearMsg", "a", "field_a")

        pair = self._read_json(path)["pairs"][0]
        self.assertEqual(pair["field_mapping_by_obf"], {"a": "field_a"})

    def test_replaces_existing_non_obf_field_mapping(self) -> None:
        path = self._temp_path()
        path.write_text(
            json.dumps(
                {
                    "pairs": [
                        {
                            "obf": "obf.Msg",
                            "non_obf": "ClearMsg",
                            "field_mapping_by_obf": {"old": "field_a"},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        upsert_pinned_field_mapping(path, "obf.Msg", "ClearMsg", "a", "field_a")

        pair = self._read_json(path)["pairs"][0]
        self.assertEqual(pair["field_mapping_by_obf"], {"a": "field_a"})

    def test_preserves_other_pairs(self) -> None:
        path = self._temp_path()
        path.write_text(
            json.dumps(
                {
                    "pairs": [
                        {"obf": "other.Obf", "non_obf": "OtherClear"},
                        {"obf": "obf.Msg", "non_obf": "ClearMsg"},
                    ]
                }
            ),
            encoding="utf-8",
        )

        upsert_pinned_field_mapping(path, "obf.Msg", "ClearMsg", "a", "field_a")

        self.assertEqual(len(self._read_json(path)["pairs"]), 2)

    def _temp_path(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return Path(temp_dir.name) / "pinned_pairs.json"

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))
