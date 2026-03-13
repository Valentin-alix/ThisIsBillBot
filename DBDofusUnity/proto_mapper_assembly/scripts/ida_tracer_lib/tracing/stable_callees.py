from collections.abc import Mapping

import idaapi

from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.simulation.interproc_calls import (
    get_direct_call_target_addr,
)
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.simulation.scan_engine import build_function_scan_plan
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.state.basic_block import FunctionScanCache


def collect_stable_callees(
    func: idaapi.func_t,
    callee_identity_by_address: Mapping[int, str],
    function_scan_cache: FunctionScanCache | None = None,
) -> list[str]:
    """Deduplicate call sites because inlining changes call counts across builds."""
    identities: set[str] = set()
    for instructions in build_function_scan_plan(func, function_scan_cache).instructions_by_block.values():
        for decoded in instructions:
            if decoded.mnemonic != "call":
                continue
            target_address = get_direct_call_target_addr(decoded.insn)
            if target_address is None:
                continue
            identity = callee_identity_by_address.get(target_address)
            if identity is not None:
                identities.add(identity)
    return sorted(identities)
