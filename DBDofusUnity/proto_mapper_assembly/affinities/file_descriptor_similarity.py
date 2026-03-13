import numpy as np

from DBDofusUnity.proto_mapper_assembly.affinities._group_similarity import build_group_scores_matrix
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace


def build_file_descriptor_similarity(
    *,
    workspace: MatchingWorkspace,
    base_scores_matrix: np.ndarray,
) -> tuple[np.ndarray, dict[tuple[str, str], float]]:
    """Return the broadcast message affinity matrix and confidence lookup per file-descriptor pair."""
    non_obf_index_by_cls = workspace.signature_indexes.non_obf_index_by_cls
    obf_index_by_cls = workspace.signature_indexes.obf_index_by_cls
    non_obf_fds = workspace.non_obf_group_descriptors
    obf_fds = workspace.obf_group_descriptors
    non_obf_fd_index = {file_descriptor: index for index, file_descriptor in enumerate(non_obf_fds)}
    obf_fd_index = {file_descriptor: index for index, file_descriptor in enumerate(obf_fds)}

    non_obf_rows_by_fd = {
        file_descriptor: [non_obf_index_by_cls[signature.message_cls] for signature in group]
        for file_descriptor, group in workspace.non_obf_groups.items()
    }
    obf_cols_by_fd = {
        file_descriptor: [obf_index_by_cls[signature.message_cls] for signature in group]
        for file_descriptor, group in workspace.obf_groups.items()
    }

    fd_similarity_matrix = build_group_scores_matrix(
        base_scores_matrix=base_scores_matrix,
        non_obf_groups=[non_obf_rows_by_fd[file_descriptor] for file_descriptor in non_obf_fds],
        obf_groups=[obf_cols_by_fd[file_descriptor] for file_descriptor in obf_fds],
    )
    fd_similarity_by_pair: dict[tuple[str, str], float] = {
        (non_obf_fd, obf_fd): float(fd_similarity_matrix[non_obf_fd_index[non_obf_fd], obf_fd_index[obf_fd]])
        for non_obf_fd in non_obf_fds
        for obf_fd in obf_fds
    }

    if not non_obf_fds or not obf_fds:
        return np.zeros_like(base_scores_matrix), fd_similarity_by_pair

    row_fd_indices = np.array(
        [non_obf_fd_index[signature.file_descriptor] for signature in workspace.non_obf_signatures]
    )
    col_fd_indices = np.array(
        [obf_fd_index[signature.file_descriptor] for signature in workspace.obf_signatures]
    )
    broadcast_matrix = fd_similarity_matrix[np.ix_(row_fd_indices, col_fd_indices)]
    return broadcast_matrix, fd_similarity_by_pair
