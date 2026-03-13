from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace, MatchResult, PreparedScoreData
from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs, MatchingRunConfig
from DBDofusUnity.proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from DBDofusUnity.proto_mapper_assembly.matching.message_selection import match_all_signatures_iteratively
from DBDofusUnity.proto_mapper_assembly.matching.score_preparation import build_prepared_scores
from DBDofusUnity.proto_mapper_assembly.matching.workspace import build_matching_workspace


def match_messages(*, inputs: MatchingInputs, run_config: MatchingRunConfig) -> tuple[MatchResult, ...]:
    print("Building matching workspace")
    workspace = build_matching_workspace(
        obf_signatures=tuple(inputs.obf_signatures_by_cls.values()),
        non_obf_signatures=tuple(inputs.non_obf_signatures_by_cls.values()),
        obf_messages_by_cls=inputs.obf_messages_by_cls,
        non_obf_messages_by_cls=inputs.non_obf_messages_by_cls,
    )
    prepared_scores = build_prepared_scores(workspace=workspace, inputs=inputs, run_config=run_config)
    return select_grouped_matches(
        workspace=workspace,
        prepared_scores=prepared_scores,
        inputs=inputs,
        run_config=run_config,
    )


def select_grouped_matches(
    *,
    workspace: MatchingWorkspace,
    prepared_scores: PreparedScoreData,
    inputs: MatchingInputs,
    run_config: MatchingRunConfig,
) -> tuple[MatchResult, ...]:
    matching_store = IterativeMatchingStore()
    matches = match_all_signatures_iteratively(
        workspace=workspace,
        prepared_scores=prepared_scores,
        matching_store=matching_store,
        inputs=inputs,
        run_config=run_config,
    )
    matches.sort(key=lambda match: match.non_obf_signature.message_cls)
    return tuple(matches)
