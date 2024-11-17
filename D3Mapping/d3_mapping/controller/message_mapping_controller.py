import json
from collections import defaultdict
from datetime import datetime

from pydantic import RootModel

from D3Mapping.d3_mapping.consts import (
    MAPPING_CONN_PROTO_PATH,
    MAPPING_GAME_AUDIT_PATH,
    MAPPING_GAME_PROTO_PATH,
    UNMAPPED_CANDIDATES_PATH,
    USED_FIELDS_PATH,
)
from D3Mapping.d3_mapping.models.mapping_info import (
    AuditHeader,
    FieldAuditInfo,
    MappingAudit,
    MessageAuditInfo,
    OutputMappingInfo,
)
from D3Mapping.d3_mapping.models.mapping_metrics import MappingMetrics


class MappingObfToClear(RootModel):
    root: dict[str, OutputMappingInfo]


class MessageMappingController:
    @staticmethod
    def dump_mapping(mapping: dict[str, OutputMappingInfo], output: str):
        with open(output, "w+") as file:
            file.write(
                MappingObfToClear(
                    dict(sorted(mapping.items(), key=lambda elem: elem[0]))
                ).model_dump_json(indent=2)
            )

    @staticmethod
    def filter_mapping_by_used_fields(
        mapping: dict[str, OutputMappingInfo],
        used_fields: dict[str, list[str]],
    ) -> dict[str, OutputMappingInfo]:
        filtered: dict[str, OutputMappingInfo] = {}

        for msg_name, info in mapping.items():
            if msg_name not in used_fields:
                continue

            used = set(used_fields[msg_name])
            filtered_field_mapping = {
                obf: clear
                for obf, clear in info.field_mapping.items()
                if clear is None or clear in used
            }

            filtered[msg_name] = OutputMappingInfo(
                obf_msg_namespace=info.obf_msg_namespace,
                field_mapping=filtered_field_mapping,
            )

        return filtered

    @staticmethod
    def get_used_fields() -> dict[str, list[str]]:
        with open(USED_FIELDS_PATH, "r") as file:
            data = json.load(file)
            return data.get("messages", {})

    @staticmethod
    def dump_audit(
        audit_by_clear_namespace: dict[str, MessageAuditInfo],
        metrics: MappingMetrics,
        output: str,
    ):
        header = AuditHeader(
            generated_at=datetime.now(),
            metrics={
                "total_comparisons": metrics.total_comparisons,
                "forced_matches": metrics.forced_matches,
                "calculated_matches": metrics.calculated_matches,
                "avg_similarity": metrics.avg_similarity,
                "validation_failures": metrics.validation_failures,
                "pulp_iterations": metrics.pulp_iterations,
                "pulp_timeouts": metrics.pulp_timeouts,
                "pulp_cycles": metrics.pulp_cycles,
                "pulp_cached_failures": metrics.pulp_cached_failures,
            },
        )
        sorted_messages = dict(
            sorted(audit_by_clear_namespace.items(), key=lambda elem: elem[0])
        )
        audit = MappingAudit(_header=header, messages=sorted_messages)
        with open(output, "w+") as file:
            file.write(audit.model_dump_json(indent=2, by_alias=True))

    @staticmethod
    def get_mapping_conn():
        with open(MAPPING_CONN_PROTO_PATH, "r") as file:
            return MappingObfToClear.model_validate(json.load(file)).root

    @staticmethod
    def get_mapping_game():
        with open(MAPPING_GAME_PROTO_PATH, "r") as file:
            return MappingObfToClear.model_validate(json.load(file)).root

    @staticmethod
    def get_audit_game() -> MappingAudit:
        with open(MAPPING_GAME_AUDIT_PATH, "r") as file:
            return MappingAudit.model_validate(json.load(file))

    @staticmethod
    def filter_audit_by_used_fields(
        audit: MappingAudit,
        used_fields: dict[str, list[str]],
    ) -> MappingAudit:
        filtered_messages: dict[str, MessageAuditInfo] = {}

        for msg_name, msg_audit in audit.messages.items():
            if msg_name not in used_fields:
                continue

            used = set(used_fields[msg_name])
            filtered_fields: dict[str, FieldAuditInfo] = {
                obf: field_info
                for obf, field_info in msg_audit.fields.items()
                if field_info.matched_clear_field is None
                or field_info.matched_clear_field in used
            }

            filtered_messages[msg_name] = MessageAuditInfo(
                similarity=msg_audit.similarity,
                algorithm=msg_audit.algorithm,
                validator_priority=msg_audit.validator_priority,
                fields=filtered_fields,
            )

        return MappingAudit(_header=audit.header, messages=filtered_messages)

    @staticmethod
    def dump_filtered_audit(audit: MappingAudit, output: str):
        sorted_messages = dict(sorted(audit.messages.items(), key=lambda elem: elem[0]))
        sorted_audit = MappingAudit(_header=audit.header, messages=sorted_messages)
        with open(output, "w+") as file:
            file.write(sorted_audit.model_dump_json(indent=2, by_alias=True))

    @staticmethod
    def get_unmapped_candidates_by_obf() -> dict[str, list[tuple[str, float]]]:
        with open(UNMAPPED_CANDIDATES_PATH, "r") as file:
            data: dict[str, list[dict[str, str | float]]] = json.load(file)
        result: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for clear_name, candidates in data.items():
            for candidate in candidates:
                obf_ns = str(candidate["obf_namespace"])
                similarity = float(candidate["similarity"])
                result[obf_ns].append((clear_name, similarity))
        return result
