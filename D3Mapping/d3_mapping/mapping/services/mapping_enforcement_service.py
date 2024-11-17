from dataclasses import dataclass
from typing import Callable

from D3Mapping.d3_mapping.consts import SIMILARITY_DIVERGENCE_THRESHOLD, EntryMsg
from D3Mapping.d3_mapping.models.mapping_info import MappingInfo, Percentage
from D3Mapping.d3_mapping.models.mapping_metrics import MappingMetrics
from D3Mapping.d3_mapping.models.p_message import PField, PMessage
from D3Mapping.d3_mapping.utils import set_percentage


@dataclass
class MappingEnforcementService:
    """Service for enforcing verified mappings on fields and messages.

    This service ensures that verified mappings (from manual validation) are
    respected during the comparison process, and tracks metrics about forced matches.
    """

    verified_msg_by_obf: dict[str, str]
    verified_msg_by_clear: dict[str, str]
    verified_mapping_field_by_clear: dict[str, dict[str, str]]
    added_mapping_by_obf_namespaces: dict[str, MappingInfo]
    metrics: MappingMetrics

    def _should_force_field_match(
        self, clear_msg: PMessage, clear_field: PField, obf_field: PField
    ) -> bool | None:
        """Check if field match should be forced based on verified mapping."""
        if clear_msg.name not in self.verified_mapping_field_by_clear:
            return None

        verified_obf_by_clear_fields = self.verified_mapping_field_by_clear[
            clear_msg.name
        ]
        if clear_field.name not in verified_obf_by_clear_fields:
            return None

        return verified_obf_by_clear_fields[clear_field.name] == obf_field.name

    def enforce_field_comparison(
        self,
        sim: Percentage,
        mapping_info: MappingInfo | None,
        clear_msg: PMessage,
        clear_field: PField,
        obf_field: PField,
    ) -> tuple[Percentage, MappingInfo | None]:
        """Enforce field comparison rules and track metrics.

        Args:
            sim: Calculated similarity
            mapping_info: Mapping info from comparison
            clear_msg: Clear message
            clear_field: Clear field
            obf_field: Obfuscated field

        Returns:
            Tuple of (enforced_similarity, mapping_info)
        """
        forced_match = self._should_force_field_match(clear_msg, clear_field, obf_field)
        if forced_match is not None:
            original_sim = sim
            sim = 1 if forced_match else 0
            self.metrics.add_comparison(sim, was_forced=True)
            if (
                forced_match
                and abs(original_sim - sim) > SIMILARITY_DIVERGENCE_THRESHOLD
            ):
                print(
                    f"⚠️  {clear_msg.name}.{clear_field.name} -> {obf_field.name} (calculated: {original_sim:.2f})"
                )
        else:
            self.metrics.add_comparison(sim, was_forced=False)

        return sim, mapping_info

    def enforce_message_comparison(
        self,
        clear_msg: PMessage,
        obf_msg: PMessage,
        compare_func: Callable,
        treated_clear_namespaces: set[str],
    ) -> MappingInfo:
        """Enforce message comparison rules based on verified mappings.

        Args:
            clear_msg: Clear message
            obf_msg: Obfuscated message
            compare_func: Function to call for actual comparison
            treated_clear_namespaces: Set of already treated namespaces

        Returns:
            MappingInfo with enforced similarity
        """
        # Check if already mapped
        if obf_msg.namespace in self.added_mapping_by_obf_namespaces:
            obf_mapping_info = self.added_mapping_by_obf_namespaces[obf_msg.namespace]
            if obf_mapping_info.clear_msg_namespace == clear_msg.namespace:
                return obf_mapping_info
            else:
                return MappingInfo(
                    similarity=0,
                    clear_msg_namespace=clear_msg.namespace,
                    field_mapping={},
                )

        is_an_entry_msg = any(
            clear_msg.namespace.endswith(entry_msg) for entry_msg in EntryMsg
        )

        mapping_info: MappingInfo
        if (
            is_an_entry_msg
            and clear_msg.name in self.verified_msg_by_clear
            and obf_msg.name != self.verified_msg_by_clear[clear_msg.name]
        ):
            mapping_info = MappingInfo(
                similarity=0,
                clear_msg_namespace=clear_msg.namespace,
                field_mapping={},
            )
        elif (
            obf_msg.name in self.verified_msg_by_obf
            and clear_msg.name != self.verified_msg_by_obf[obf_msg.name]
        ):
            mapping_info = MappingInfo(
                similarity=0,
                clear_msg_namespace=clear_msg.namespace,
                field_mapping={},
            )
        elif len(clear_msg.elements) == 0 and len(obf_msg.elements) == 0:
            mapping_info = MappingInfo(
                similarity=1,
                clear_msg_namespace=clear_msg.namespace,
                field_mapping={},
            )
        elif (len(clear_msg.elements) == 0) != (len(obf_msg.elements) == 0):
            mapping_info = MappingInfo(
                similarity=0,
                clear_msg_namespace=clear_msg.namespace,
                field_mapping={},
            )
        else:
            mapping_info = compare_func(clear_msg, obf_msg, treated_clear_namespaces)
            if is_an_entry_msg and clear_msg.name in self.verified_msg_by_clear:
                mapping_info.similarity = (
                    0
                    if obf_msg.name != self.verified_msg_by_clear[clear_msg.name]
                    else 1
                )
            if obf_msg.name in self.verified_msg_by_obf:
                mapping_info.similarity = (
                    0 if clear_msg.name != self.verified_msg_by_obf[obf_msg.name] else 1
                )

        mapping_info.similarity = set_percentage(mapping_info.similarity)
        return mapping_info
