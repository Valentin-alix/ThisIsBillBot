import json
from pathlib import Path

from src.gui.pages.debugs.message_detail import resolve_selected_pinned_field
from src.gui.pages.debugs.sniffer import (
    _resolve_child_pinned_message_pair,
    _upsert_pinned_field_mapping_with_child_pair,
)
from src.protocol.message_names import find_non_obf_game_message_descriptor


class TestPinnedFieldResolution:
    def test_selected_message_field_exposes_child_descriptor(self) -> None:
        descriptor = find_non_obf_game_message_descriptor(
            "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionItemListEvent"
        )
        assert descriptor is not None

        selected_field = resolve_selected_pinned_field(descriptor, ("actions",))

        assert selected_field is not None
        assert selected_field.field_descriptor is descriptor.fields_by_name["actions"]
        assert selected_field.message_descriptor is not None
        assert (
            selected_field.message_descriptor.full_name
            == "com.ankama.dofus.server.game.protocol.common.GameActionItem"
        )

    def test_message_fields_create_child_pinned_pair(self) -> None:
        descriptor = find_non_obf_game_message_descriptor(
            "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionItemListEvent"
        )
        assert descriptor is not None
        selected_field = resolve_selected_pinned_field(descriptor, ("actions",))
        assert selected_field is not None

        child_pair = _resolve_child_pinned_message_pair(selected_field, selected_field)

        assert child_pair == (
            "com.ankama.dofus.server.game.protocol.common.GameActionItem",
            "Com.Ankama.Dofus.Server.Game.Protocol.Common.GameActionItem",
        )

    def test_message_field_mapping_persists_parent_and_child_pairs(
        self, tmp_path: Path
    ) -> None:
        descriptor = find_non_obf_game_message_descriptor(
            "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionItemListEvent"
        )
        assert descriptor is not None
        selected_field = resolve_selected_pinned_field(descriptor, ("actions",))
        assert selected_field is not None
        pinned_pairs_path = tmp_path / "pinned_pairs.json"

        _upsert_pinned_field_mapping_with_child_pair(
            pinned_pairs_path,
            (
                "obf.parent.Message",
                "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionItemListEvent",
            ),
            selected_field,
            selected_field,
        )

        assert json.loads(pinned_pairs_path.read_text(encoding="utf-8")) == {
            "pairs": [
                {
                    "obf": "obf.parent.Message",
                    "non_obf": "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionItemListEvent",
                    "field_mapping_by_obf": {"actions": "actions"},
                },
                {
                    "obf": "com.ankama.dofus.server.game.protocol.common.GameActionItem",
                    "non_obf": "Com.Ankama.Dofus.Server.Game.Protocol.Common.GameActionItem",
                },
            ]
        }

    def test_scalar_fields_do_not_create_child_pinned_pair(self) -> None:
        descriptor = find_non_obf_game_message_descriptor(
            "Com.Ankama.Dofus.Server.Game.Protocol.Gamemap.MapChangeRequest"
        )
        assert descriptor is not None
        selected_field = resolve_selected_pinned_field(descriptor, ("map_id",))
        assert selected_field is not None

        assert (
            _resolve_child_pinned_message_pair(selected_field, selected_field) is None
        )
