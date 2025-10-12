from pydantic import BaseModel, RootModel

from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping_rejected_infos import FieldMappingRejectedInfos


class GameMappingEntry(BaseModel):
    full_obf_msg_namespace: str
    obf_msg_namespace: str
    full_non_obf_msg_namespace: str
    field_mapping: dict[str, str]
    field_mapping_infos: dict[str, dict[str, float]]
    field_mapping_rejected_infos: FieldMappingRejectedInfos
    field_mapping_unmapped_non_obf_fields: dict[str, str]
    similarity_score: float
    group_similarity_score: float
    assembly_similarity_score: float
    structure_similarity_score: float
    runtime_confidence: float | None
    match_margin: float
    runner_up_obf: str | None
    is_low_confidence: bool
    evidence_coverage: float | None
    is_runtime_observed: bool = False


class GameMappingsDocument(RootModel[dict[str, GameMappingEntry]]):
    root: dict[str, GameMappingEntry]


class SimpleGameMappingEntry(BaseModel):
    obf_msg_namespace: str
    field_mapping: dict[str, str]


class SimpleGameMappingsDocument(RootModel[dict[str, SimpleGameMappingEntry]]):
    root: dict[str, SimpleGameMappingEntry]
