from __future__ import annotations

from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace, MatchResult, PreparedScoreData
from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs, MatchingRunConfig
from DBDofusUnity.proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from DBDofusUnity.proto_mapper_assembly.matching.message_selection import match_all_signatures_iteratively
from DBDofusUnity.proto_mapper_assembly.matching.score_preparation import build_prepared_scores
from DBDofusUnity.proto_mapper_assembly.matching.workspace import build_matching_workspace


def match_messages(*, inputs: MatchingInputs, run_config: MatchingRunConfig) -> tuple[MatchResult, ...]:
    """
    Map every obfuscated message onto a non-obfuscated one, in three phases.

    1. ``build_matching_workspace`` freezes the two signature sets and precomputes the lookups.
    2. ``build_prepared_scores`` turns them into one score per candidate pair.
    3. ``select_grouped_matches`` commits pairs, best first, until nothing credible is left.
    """
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
    """
    Select message matches globally.

    File-descriptor similarity is baked into ``prepared_scores`` as a soft score
    multiplier, so a single global iterative pass spans all files at once. Pinned pairs
    are enforced through their hard matrix overrides (score 1.0 with the rest of their
    row/column zeroed), so the global best-first selection picks them first.
    """
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
