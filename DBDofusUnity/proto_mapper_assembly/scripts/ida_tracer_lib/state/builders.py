from __future__ import annotations

from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.signatures.types import ProtoParameterSeed
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.state.types import (
    FIRST_STACK_PARAM_OFFSET,
    WINDOWS_X64_PARAM_REGISTERS,
    HeapState,
    RegisterState,
    StackFrameState,
    StackState,
)


def build_initial_register_state(
    proto_parameter_seeds: list[ProtoParameterSeed],
    has_this: bool,
    this_class_name: str | None = None,
) -> RegisterState:
    """
    Build initial register state from proto parameter positions.

    For instance methods, rcx holds 'this', so explicit params start at rdx.
    For static methods, explicit params start at rcx.
    """
    reg_state: RegisterState = {}
    if has_this and this_class_name is not None:
        reg_state[WINDOWS_X64_PARAM_REGISTERS[0]] = ("object", this_class_name)
    first_explicit_param_register_index = 1 if has_this else 0
    for param_index, tracked_domain, class_name in proto_parameter_seeds:
        register_list_index = param_index + first_explicit_param_register_index
        if register_list_index >= len(WINDOWS_X64_PARAM_REGISTERS):
            break
        reg_num = WINDOWS_X64_PARAM_REGISTERS[register_list_index]
        reg_state[reg_num] = (tracked_domain, class_name)
    return reg_state


def build_initial_stack_state(
    proto_parameter_seeds: list[ProtoParameterSeed],
    has_this: bool,
) -> StackState:
    """
    Build an entry-stack view for proto params passed after r9.

    The callee sees the first stack argument at [rsp+0x28] on Windows x64.
    The first explicit stack parameter index is 3 for instance methods and 4
    for static methods because static calls can use rcx as a real parameter.
    """
    stack_state: StackState = {}
    first_stack_param_index = len(WINDOWS_X64_PARAM_REGISTERS) - (1 if has_this else 0)
    for param_index, tracked_domain, class_name in proto_parameter_seeds:
        if param_index < first_stack_param_index:
            continue
        stack_offset = FIRST_STACK_PARAM_OFFSET + ((param_index - first_stack_param_index) * 8)
        stack_state[stack_offset] = (tracked_domain, class_name)
    return stack_state


def build_initial_frame_state() -> StackFrameState:
    return StackFrameState()


def build_initial_heap_state() -> HeapState:
    return {}
