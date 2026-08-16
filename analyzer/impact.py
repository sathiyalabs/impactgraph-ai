import networkx as nx


def find_impacted_files(
    graph: nx.DiGraph,
    changed_file: str,
) -> set[str]:
    """
    Find all files that may be affected by a change.

    The graph contains edges:
        A -> B

    meaning:
        A depends on B.

    Therefore, when B changes, we need to look
    backwards through the graph to find its dependents.
    """

    if changed_file not in graph:
        raise ValueError(
            f"File '{changed_file}' does not exist in the dependency graph."
        )

    impacted_files = set()

    # Start with files that directly depend on the changed file.
    queue = list(graph.predecessors(changed_file))

    while queue:
        current_file = queue.pop(0)

        if current_file in impacted_files:
            continue

        impacted_files.add(current_file)

        # Find files that depend on the current file.
        for predecessor in graph.predecessors(current_file):
            if predecessor not in impacted_files:
                queue.append(predecessor)

    return impacted_files