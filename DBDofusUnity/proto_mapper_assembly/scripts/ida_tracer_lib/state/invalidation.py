from __future__ import annotations

from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.state.types import (
    WINDOWS_X64_VOLATILE_REGISTERS,
    HeapState,
    RegisterState,
)


def invalidate_volatile_registers(reg_state: RegisterState) -> None:
    """Drop tracked values from caller-saved registers after a call."""
    for register_number in WINDOWS_X64_VOLATILE_REGISTERS:
        reg_state.pop(register_number, None)


def invalidate_heap_slots_for_register(heap_state: HeapState, register_number: int) -> None:
    """Purge heap slots whose base register has been clobbered."""
    stale_slots = [slot for slot in heap_state if slot[0] == register_number]
    for slot in stale_slots:
        heap_state.pop(slot, None)


def invalidate_heap_slots_for_volatile_bases(heap_state: HeapState) -> None:
    """Purge heap slots whose base is a caller-saved register (value unknown after a call)."""
    stale_slots = [slot for slot in heap_state if slot[0] in WINDOWS_X64_VOLATILE_REGISTERS]
    for slot in stale_slots:
        heap_state.pop(slot, None)
