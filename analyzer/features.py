from pathlib import Path

import networkx as nx

from analyzer.impact import find_impacted_files


def build_change_features(
    graph: nx.DiGraph,
    changed_files: list[str],
    change_metrics: dict[str, dict[str, int]],
) -> list[dict]:
    """
    Combine Git change metrics with dependency-impact metrics.

    Returns one feature record for every changed file.
    """

    normalized_graph_files = {
        node.replace("\\", "/"): node
        for node in graph.nodes
    }

    features = []

    for changed_file in changed_files:
        normalized_changed_file = changed_file.replace("\\", "/")

        graph_file = normalized_graph_files.get(
            normalized_changed_file
        )

        if graph_file is None:
            continue

        impacted_files = find_impacted_files(
            graph,
            graph_file,
        )

        direct_impacts = len(
            list(graph.predecessors(graph_file))
        )

        indirect_impacts = max(
            0,
            len(impacted_files) - direct_impacts,
        )

        metrics = change_metrics.get(
            normalized_changed_file,
            {},
        )

        record = {
            "file": normalized_changed_file,
            "lines_added": metrics.get(
                "lines_added",
                0,
            ),
            "lines_deleted": metrics.get(
                "lines_deleted",
                0,
            ),
            "total_changes": metrics.get(
                "total_changes",
                0,
            ),
            "direct_impacts": direct_impacts,
            "indirect_impacts": indirect_impacts,
            "total_impacts": len(impacted_files),
        }

        features.append(record)

    return features