"""Constants for mapping error and warning messages."""

# PuLP Solver messages
from D3Mapping.d3_mapping.models.mapping_info import OutputMappingInfo

PULP_MAX_ITERATIONS_REACHED = "Max iterations reached for {clear_name} <-> {obf_name}"
PULP_CONSTRAINTS_TRIED = "Constraints tried: {count}"
PULP_CYCLE_DETECTED = "Constraint cycle detected for {clear_name}"
PULP_CONVERSION_ERROR = "Error converting PuLP result for {clear_name}: {error}"

# Validation messages
NOT_ENOUGH_REGISTERED_MSG = "Not enough registered msg for {clear_name} with obf_msg {obf_name}"

# Forced match warnings
FORCED_MATCH_DIVERGENCE = "{clear_msg}.{clear_field} -> {obf_field} (calculated: {sim:.2f})"


def format_pulp_timeout(clear_name: str, obf_name: str, constraints_count: int) -> str:
    """Format the PuLP timeout message."""
    msg = PULP_MAX_ITERATIONS_REACHED.format(clear_name=clear_name, obf_name=obf_name)
    constraints = PULP_CONSTRAINTS_TRIED.format(count=constraints_count)
    return f"{msg}\n   {constraints}"


def format_forced_match_warning(
    clear_msg_name: str, clear_field_name: str, obf_field_name: str, similarity: float
) -> str:
    """Format the forced match divergence warning."""
    return FORCED_MATCH_DIVERGENCE.format(
        clear_msg=clear_msg_name,
        clear_field=clear_field_name,
        obf_field=obf_field_name,
        sim=similarity,
    )


def diff_output_field_mappings(
    mapping_dict_a: dict[str, OutputMappingInfo],
    mapping_dict_b: dict[str, OutputMappingInfo],
    useful_message_names: list[str] = [
        "GameActionFightEvent",
        "CharacterCharacteristicDetailedUsable",
    ],
) -> list[str]:
    differences: list[str] = []

    # Indexer les structures par clear_msg_namespace pour comparer correctement
    namespace_to_mapping_a = {mapping.obf_msg_namespace: mapping for mapping in mapping_dict_a.values()}
    namespace_to_mapping_b = {mapping.obf_msg_namespace: mapping for mapping in mapping_dict_b.values()}

    # Parcourir uniquement les namespaces communs
    for namespace in namespace_to_mapping_a.keys() & namespace_to_mapping_b.keys():
        if namespace.split(".")[-1] not in useful_message_names:
            continue
        mapping_a = namespace_to_mapping_a[namespace]
        mapping_b = namespace_to_mapping_b[namespace]

        # Construire dictionnaire champ_métier -> clé_obfusquée
        field_to_key_a = {
            field_name: obfuscated_key
            for obfuscated_key, value in mapping_a.field_mapping.items()
            if value is not None
            for _, field_name in [value]
        }

        field_to_key_b = {
            field_name: obfuscated_key
            for obfuscated_key, value in mapping_b.field_mapping.items()
            if value is not None
            for _, field_name in [value]
        }

        # Comparer les clés pour chaque champ métier
        for field_name in field_to_key_a.keys() & field_to_key_b.keys():
            key_in_a = field_to_key_a[field_name]
            key_in_b = field_to_key_b[field_name]

            if key_in_a != key_in_b:
                differences.append(f"[{namespace.split('.')[-1]}] {field_name} : from {key_in_a} to {key_in_b}")

    return differences
