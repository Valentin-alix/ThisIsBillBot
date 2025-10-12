from __future__ import annotations

from DBDofusUnity.proto_mapper_assembly.controllers import non_obf_bootstrap, signature_override_application
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import SignatureOverrideEntry


def prepare_non_obf_matching_inputs(
    *,
    overrides: dict[str, SignatureOverrideEntry],
    bootstrap_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature],
    non_obf_enum_signatures_by_name: dict[str, EnumSignatureEntry],
) -> tuple[dict[str, DumpCSMessage], dict[str, MessageAccessSignature]]:
    overlay = non_obf_bootstrap.build_bootstrap_message_overlay(
        bootstrap_messages_by_cls=bootstrap_messages_by_cls,
        non_obf_messages_by_cls=non_obf_messages_by_cls,
    )
    overridden_signatures_by_cls = non_obf_bootstrap.rewire_signatures_to_bootstrap_messages(
        messages_by_cls=overlay.messages_by_cls,
        non_obf_signatures_by_cls=non_obf_signatures_by_cls,
    )
    prepared_messages_by_cls, prepared_signatures_by_cls = (
        non_obf_bootstrap.inject_synthetic_non_obf_entries_for_override_only_messages(
            overrides=overrides,
            bootstrap_messages_by_cls=bootstrap_messages_by_cls,
            non_obf_messages_by_cls=overlay.messages_by_cls,
            non_obf_signatures_by_cls=overridden_signatures_by_cls,
        )
    )
    prepared_signatures_by_cls = signature_override_application.apply_stored_signature_overrides(
        non_obf_signatures_by_cls=prepared_signatures_by_cls,
        overrides=overrides,
        non_obf_enum_signatures_by_name=non_obf_enum_signatures_by_name,
    )
    return prepared_messages_by_cls, prepared_signatures_by_cls
