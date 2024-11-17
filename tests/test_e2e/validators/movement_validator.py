from dataclasses import dataclass
from typing import TypedDict

from D3Database.grid.map_point import MapPoint
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapMovementConfirmRequest,
    MapMovementEvent,
    MapMovementRequest,
)

from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from tests.test_e2e.validators.base import (
    RecordedMessage,
    SequenceValidator,
    ValidationResult,
)


class MovementSequence(TypedDict):
    request: RecordedMessage
    event: RecordedMessage
    confirm: RecordedMessage


@dataclass
class MovementValidator(SequenceValidator):
    character_id: int
    inventory_weight: int
    inventory_weight_max: int
    pathfinding: Pathfinding
    timing_tolerance_ms: float = 50

    def applies_to(self, messages: list[RecordedMessage]) -> bool:
        type_names = [m.msg_type_name for m in messages]
        return "MapMovementRequest" in type_names and "MapMovementEvent" in type_names

    def validate(self, messages: list[RecordedMessage]) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        movement_sequences = self._extract_movement_sequences(messages)

        for seq in movement_sequences:
            results.extend(self._validate_sequence(seq))

        return results

    def _extract_movement_sequences(
        self, messages: list[RecordedMessage]
    ) -> list[MovementSequence]:
        sequences: list[MovementSequence] = []
        current_seq: dict[str, RecordedMessage] = {}

        for msg in messages:
            if isinstance(msg.msg, MapMovementRequest):
                current_seq = {"request": msg}
            elif isinstance(msg.msg, MapMovementEvent):
                if current_seq and msg.msg.character_id == self.character_id:
                    current_seq["event"] = msg
            elif isinstance(msg.msg, MapMovementConfirmRequest):
                if current_seq and "event" in current_seq:
                    current_seq["confirm"] = msg
                    sequences.append(
                        MovementSequence(
                            request=current_seq["request"],
                            event=current_seq["event"],
                            confirm=current_seq["confirm"],
                        )
                    )
                    current_seq = {}

        return sequences

    def _validate_sequence(self, seq: MovementSequence) -> list[ValidationResult]:
        results: list[ValidationResult] = []

        request: MapMovementRequest = seq["request"].msg  # type: ignore[assignment]
        event: MapMovementEvent = seq["event"].msg  # type: ignore[assignment]
        confirm_msg = seq["confirm"]
        event_msg = seq["event"]

        results.append(self._validate_key_cells(request, event))
        results.append(self._validate_timing(event_msg, confirm_msg, event))

        return results

    def _validate_key_cells(
        self, request: MapMovementRequest, event: MapMovementEvent
    ) -> ValidationResult:
        cells = list(event.cells)
        if len(cells) < 2:
            return ValidationResult(
                is_valid=True, reason="Single cell movement, no path to validate"
            )

        start_cell = cells[0]
        end_cell = cells[-1]

        start_mp = MapPoint.from_cell_id(start_cell)
        end_mp = MapPoint.from_cell_id(end_cell)

        expected_path = self.pathfinding.find_path(start_mp, {end_mp})
        if expected_path is None:
            return ValidationResult(
                is_valid=False,
                reason=f"Pathfinding failed for {start_cell} -> {end_cell}",
                details={"start": start_cell, "end": end_cell},
            )

        expected_key_cells = expected_path.get_key_cells()
        actual_key_cells = list(request.key_cells)

        if actual_key_cells != expected_key_cells:
            return ValidationResult(
                is_valid=False,
                reason="key_cells mismatch",
                details={
                    "actual": actual_key_cells,
                    "expected": expected_key_cells,
                    "start": start_cell,
                    "end": end_cell,
                },
            )

        return ValidationResult(is_valid=True, reason="key_cells match")

    def _validate_timing(
        self,
        event_msg: RecordedMessage,
        confirm_msg: RecordedMessage,
        event: MapMovementEvent,
    ) -> ValidationResult:
        cells = list(event.cells)
        path_elements = MovementPath.get_path_elements_from_cells(cells)

        expected_duration = MovementPath.get_total_duration(
            path_elements,
            self.inventory_weight,
            self.inventory_weight_max,
        )

        actual_duration = confirm_msg.timestamp - event_msg.timestamp
        diff_ms = abs(actual_duration - expected_duration) * 1000

        if diff_ms > self.timing_tolerance_ms:
            return ValidationResult(
                is_valid=False,
                reason=f"Timing mismatch: {diff_ms:.0f}ms difference",
                details={
                    "actual_duration_s": actual_duration,
                    "expected_duration_s": expected_duration,
                    "diff_ms": diff_ms,
                    "tolerance_ms": self.timing_tolerance_ms,
                },
            )

        return ValidationResult(
            is_valid=True,
            reason=f"Timing OK (diff: {diff_ms:.0f}ms)",
            details={
                "actual_duration_s": actual_duration,
                "expected_duration_s": expected_duration,
            },
        )
