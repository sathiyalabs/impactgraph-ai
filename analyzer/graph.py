import networkx as nx
from pathlib import Path

from analyzer.parser import find_python_files, extract_imports


def build_dependency_graph(repository_path: str) -> nx.DiGraph:
    """
    Build a directed dependency graph for a Python repository.

    Nodes:
        Python files

    Edges:
        A -> B means A imports B.
    """
    graph = nx.DiGraph()

    files = find_python_files(repository_path)

    # Add every Python file as a graph node.
    for file in files:
        relative_path = file.relative_to(repository_path)
        graph.add_node(str(relative_path))

    # Add dependency edges.
    for file in files:
        current_file = str(file.relative_to(repository_path))

        imports = extract_imports(file)

        for imported_module in imports:
            imported_path = imported_module.replace(".", "/") + ".py"

            for node in graph.nodes:
                normalized_node = node.replace("\\", "/")

                if normalized_node.endswith(imported_path):
                    graph.add_edge(current_file, node)

    return graph