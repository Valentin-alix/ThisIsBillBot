from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import builder_field_access_entry

from proto_mapper_assembly.interfaces.assembly_access import AccessEntry, AccessKind, FieldAccessEntry
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField
from proto_mapper_assembly.interfaces.il2cpp_json import Il2CppApiDefinition, MethodDefinition
from proto_mapper_assembly.scripts.ida_tracer_lib.lookups.accessor_candidate import AccessorCandidate
from proto_mapper_assembly.scripts.ida_tracer_lib.simulation.field_access import (
    collect_instruction_field_accesses,
)
from proto_mapper_assembly.scripts.ida_tracer_lib.state.analysis_state import AnalysisState
from proto_mapper_assembly.scripts.ida_tracer_lib.state.builders import build_initial_frame_state
from proto_mapper_assembly.scripts.ida_tracer_lib.state.register_updates import (
    update_stack_frame_for_instruction,
)

if TYPE_CHECKING:
    import proto_mapper_assembly.scripts.ida_tracer_lib.typings.idaapi as idaapi_types
    from proto_mapper_assembly.scripts.ida_tracer_lib.state.types import (
        HeapState,
        RegisterState,
        StackFrameState,
        StackState,
    )

    type InsnT = idaapi_types.insn_t
else:
    type InsnT = object

# Windows x64 register indices (IDA)
RAX_REG: int = 0
RCX_REG: int = 1
RDX_REG: int = 2
RBX_REG: int = 3
RSP_REG: int = 4
RBP_REG: int = 5
RDI_REG: int = 7
R8_REG: int = 8
R9_REG: int = 9
R10_REG: int = 10
R14_REG: int = 14
R15_REG: int = 15
XMM0_REG: int = 33

# IDA operand type constants (matching idaapi values)
MOCK_O_REG: int = 1
MOCK_O_MEM: int = 2
MOCK_O_PHRASE: int = 3
MOCK_O_DISPL: int = 4
MOCK_O_IMM: int = 5
MOCK_O_NEAR: int = 7
MOCK_O_FAR: int = 8
NON_MATCHING_OP: int = 0


class MockOp:
    def __init__(
        self,
        op_type: int,
        *,
        reg: int = 0,
        addr: int = 0,
        value: int = 0,
        dtype: int | None = None,
    ) -> None:
        self.type = op_type
        self.reg = reg
        self.addr = addr
        self.value = value
        self.dtype = dtype


class MockInsn:
    def __init__(self, dst: MockOp, src: MockOp, mnemonic: str = "mov") -> None:
        self._mnemonic = mnemonic
        self.ops: list[MockOp] = [dst, src]

    def get_canon_mnem(self) -> str:
        return self._mnemonic


class MockCallInsn:
    def __init__(self, op: MockOp) -> None:
        self._mnemonic = "call"
        self.ops: list[MockOp] = [op, MockOp(NON_MATCHING_OP)]

    def get_canon_mnem(self) -> str:
        return self._mnemonic


def as_insn(insn: object) -> InsnT:
    return cast("InsnT", insn)


def mock_insn(mnemonic: str, dst: MockOp, src: MockOp) -> MockInsn:
    return MockInsn(dst, src, mnemonic=mnemonic)


def empty_type_lookup() -> dict[str, str]:
    return {}


def apply_standard_frame_setup(frame_state: StackFrameState, stack_allocation: int = 0) -> None:
    update_stack_frame_for_instruction(
        as_insn(MockInsn(MockOp(MOCK_O_REG, reg=RBP_REG), MockOp(NON_MATCHING_OP), mnemonic="push")),
        frame_state,
    )
    update_stack_frame_for_instruction(
        as_insn(MockInsn(MockOp(MOCK_O_REG, reg=RBP_REG), MockOp(MOCK_O_REG, reg=RSP_REG))),
        frame_state,
    )
    if stack_allocation == 0:
        return
    update_stack_frame_for_instruction(
        as_insn(
            MockInsn(
                MockOp(MOCK_O_REG, reg=RSP_REG),
                MockOp(MOCK_O_IMM, value=stack_allocation),
                mnemonic="sub",
            )
        ),
        frame_state,
    )


def handle_mov_instruction(
    insn: object,
    reg_state: RegisterState,
    proto_fields_by_class: dict[str, dict[int, DumpCSMessageField]],
) -> list[AccessEntry]:
    return list(collect_instruction_field_accesses(as_insn(insn), 0, reg_state, proto_fields_by_class))


def accessor_candidate(
    owner_cls: str = "MyMsg",
    access_kind: AccessKind = "getter",
    field: str = "items_",
    *,
    property_name: str | None = None,
    field_offset: int = 0x18,
    clr_type: str | None = None,
    normalized_type: str | None = None,
    returned_cls: str | None = None,
    returned_domain: Literal["object", "repeated_container"] | None = None,
) -> AccessorCandidate:
    return AccessorCandidate(
        owner_cls=owner_cls,
        access_kind=access_kind,
        field=field,
        property_name=property_name or field,
        field_offset=field_offset,
        clr_type=clr_type,
        normalized_type=normalized_type,
        returned_cls=returned_cls,
        _returned_domain=returned_domain,
    )


def field_getter_entry(cls: str = "MyMsg", field: str = "items_") -> FieldAccessEntry:
    return builder_field_access_entry(
        access_kind="getter",
        cls=cls,
        field=field,
        property_name=None,
        field_offset=0x18,
    )


def field_setter_entry(cls: str = "MyMsg", field: str = "name_") -> FieldAccessEntry:
    return builder_field_access_entry(
        access_kind="setter",
        cls=cls,
        field=field,
        property_name=None,
        field_offset=0x18,
    )


class MockDecodedInsn:
    def __init__(self) -> None:
        self._mnemonic = ""
        self.ops: list[MockOp] = [MockOp(NON_MATCHING_OP), MockOp(NON_MATCHING_OP)]

    def get_canon_mnem(self) -> str:
        return self._mnemonic


class MockFunc:
    def __init__(self, start_ea: int, end_ea: int) -> None:
        self.start_ea = start_ea
        self.end_ea = end_ea


def builder_mock_func(start_ea: int, end_ea: int) -> MockFunc:
    return MockFunc(start_ea, end_ea)


class MockBasicBlock:
    def __init__(self, start_ea: int, end_ea: int) -> None:
        self.start_ea = start_ea
        self.end_ea = end_ea
        self._successors: list[MockBasicBlock] = []

    def connect(self, *successors: MockBasicBlock) -> None:
        self._successors = list(successors)

    def succs(self) -> list[MockBasicBlock]:
        return list(self._successors)


def analysis_state(
    *,
    reg_state: RegisterState,
    frame_state: StackFrameState | None = None,
    stack_state: StackState | None = None,
    heap_state: HeapState | None = None,
) -> AnalysisState:
    return AnalysisState(
        reg_state=dict(reg_state),
        frame_state=frame_state or build_initial_frame_state(),
        stack_state=dict(stack_state) if stack_state is not None else {},
        heap_state=dict(heap_state) if heap_state is not None else {},
        type_guard=None,
    )


def method_definition(
    *,
    signature: str,
    dot_net_signature: str | None,
    virtual_address: str = "0x10",
    name: str = "Describe",
    group: str = "Ankama.Dofus.Protocol.Game.dll/Owner",
) -> MethodDefinition:
    return MethodDefinition.model_validate(
        {
            "virtualAddress": virtual_address,
            "name": name,
            "signature": signature,
            "dotNetSignature": dot_net_signature,
            "group": group,
        }
    )


def api_definition(*, virtual_address: str, name: str, signature: str | None) -> Il2CppApiDefinition:
    return Il2CppApiDefinition.model_validate(
        {
            "virtualAddress": virtual_address,
            "name": name,
            "signature": signature,
        }
    )
