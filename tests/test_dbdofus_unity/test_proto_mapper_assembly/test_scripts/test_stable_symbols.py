from DBDofusUnity.proto_mapper_assembly.interfaces.il2cpp_json import MethodDefinition
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.lookups.stable_symbols import (
    build_callee_identity_lookup,
)


def _method(
    *, address: str, group: str, dot_net_signature: str | None = "Void Handle(Int32)"
) -> MethodDefinition:
    return MethodDefinition.model_validate(
        {
            "virtualAddress": address,
            "name": "_ZN4mock6methodEv",
            "signature": "void method()",
            "dotNetSignature": dot_net_signature,
            "group": group,
        }
    )


class TestStableSymbols:
    def test_readable_method_keeps_owner_and_arity_but_drops_types(self) -> None:
        lookup = build_callee_identity_lookup(
            [
                _method(
                    address="0x10",
                    group="Core.dll/Core/UILogic/Inventory/Inventory",
                    dot_net_signature="lz GetItem(Int32)",
                )
            ]
        )

        assert lookup == {0x10: "Core.dll/Core/UILogic/Inventory/Inventory::GetItem/1"}

    def test_obfuscated_owner_or_method_is_dropped(self) -> None:
        lookup = build_callee_identity_lookup(
            [
                _method(address="0x10", group="Core.dll/ba", dot_net_signature="Void Handle(Int32)"),
                _method(
                    address="0x20",
                    group="Core.dll/Core/UILogic/Inventory/Inventory",
                    dot_net_signature="Void mjx(Int32)",
                ),
            ]
        )

        assert lookup == {}

    def test_folded_addresses_are_dropped(self) -> None:
        lookup = build_callee_identity_lookup(
            [
                _method(address="0x30", group="mscorlib.dll/System/Int32"),
                _method(address="0x30", group="mscorlib.dll/System/UInt32"),
            ]
        )

        assert lookup == {}

    def test_method_without_dot_net_signature_is_dropped(self) -> None:
        lookup = build_callee_identity_lookup(
            [_method(address="0x40", group="mscorlib.dll/System/String", dot_net_signature=None)]
        )

        assert lookup == {}

    def test_parameterless_method_reports_zero_arity(self) -> None:
        lookup = build_callee_identity_lookup(
            [
                _method(
                    address="0x50",
                    group="mscorlib.dll/System/Int32",
                    dot_net_signature="String ToString()",
                )
            ]
        )

        assert lookup == {0x50: "mscorlib.dll/System/Int32::ToString/0"}
