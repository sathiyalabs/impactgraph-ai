import networkx as nx
import pytest

from analyzer.graph import build_dependency_graph
from analyzer.impact import find_impacted_files


REPOSITORY = "data/real_repos/flask"


def test_build_dependency_graph():
    """Build a dependency graph containing Python files."""

    graph = build_dependency_graph(REPOSITORY)

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() > 0

    assert (
        "src/flask/app.py" in graph
        or "src\\flask\\app.py" in graph
    )


def test_dependency_graph_contains_edges():
    """Verify that dependency relationships are discovered."""

    graph = build_dependency_graph(REPOSITORY)

    assert graph.number_of_edges() > 0


def test_find_impacted_files():
    """Find direct and transitive dependents of a changed file."""

    graph = nx.DiGraph()

    graph.add_edges_from(
        [
            ("app.py", "models.py"),
            ("routes.py", "app.py"),
            ("tests.py", "routes.py"),
        ]
    )

    impacted = find_impacted_files(
        graph,
        "models.py",
    )

    assert impacted == {
        "app.py",
        "routes.py",
        "tests.py",
    }


def test_find_impacted_files_direct_dependency():
    """Return a direct dependent of the changed file."""

    graph = nx.DiGraph()

    graph.add_edge(
        "app.py",
        "models.py",
    )

    impacted = find_impacted_files(
        graph,
        "models.py",
    )

    assert impacted == {
        "app.py",
    }


def test_find_impacted_files_missing_node():
    """Raise ValueError when the changed file is absent."""

    graph = nx.DiGraph()

    graph.add_edge(
        "app.py",
        "models.py",
    )

    with pytest.raises(ValueError):
        find_impacted_files(
            graph,
            "missing.py",
        )