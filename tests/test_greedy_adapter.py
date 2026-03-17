import numpy as np
import pytest

from hpc_framework.greedy_adapter import clusters_to_labels, observed_k_from_labels


def test_clusters_to_labels_builds_zero_based_partition_vector():
    clusters = [{0, 2}, {1, 3, 4}]
    labels = clusters_to_labels(clusters, n=5)

    assert isinstance(labels, np.ndarray)
    assert labels.shape == (5,)
    assert labels.dtype.kind in {"i", "u"}

    assert labels[0] == 0
    assert labels[2] == 0
    assert labels[1] == 1
    assert labels[3] == 1
    assert labels[4] == 1


def test_clusters_to_labels_raises_if_some_vertex_is_unassigned():
    clusters = [{0, 2}, {1}]
    with pytest.raises(ValueError, match="not assigned"):
        clusters_to_labels(clusters, n=4)


def test_clusters_to_labels_raises_if_vertex_appears_twice():
    clusters = [{0, 2}, {2, 3}]
    with pytest.raises(ValueError, match="assigned more than once"):
        clusters_to_labels(clusters, n=4)


def test_observed_k_from_labels_counts_distinct_zero_based_blocks():
    labels = np.array([0, 0, 1, 2, 2], dtype=int)
    assert observed_k_from_labels(labels) == 3
