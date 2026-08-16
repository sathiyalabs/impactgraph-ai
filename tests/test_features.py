import networkx as nx

from analyzer.features import build_change_features


def test_build_change_features():
    """Build ML features from changes and dependency impacts."""

    graph = nx.DiGraph()

    graph.add_edges_from(
        [
            ("app.py", "models.py"),
            ("routes.py", "app.py"),
            ("tests.py", "routes.py"),
        ]
    )

    changed_files = ["models.py"]

    change_metrics = {
        "models.py": {
            "lines_added": 10,
            "lines_deleted": 3,
            "total_changes": 13,
        }
    }

    features = build_change_features(
        graph,
        changed_files,
        change_metrics,
    )

    assert len(features) == 1

    record = features[0]

    assert record["file"] == "models.py"
    assert record["lines_added"] == 10
    assert record["lines_deleted"] == 3
    assert record["total_changes"] == 13

    assert record["direct_impacts"] == 1
    assert record["indirect_impacts"] == 2
    assert record["total_impacts"] == 3


def test_build_change_features_normalizes_paths():
    """Normalize Windows-style paths before graph matching."""

    graph = nx.DiGraph()

    graph.add_edge(
        "src\\app.py",
        "src\\models.py",
    )

    changed_files = [
        "src/models.py",
    ]

    change_metrics = {
        "src/models.py": {
            "lines_added": 5,
            "lines_deleted": 1,
            "total_changes": 6,
        }
    }

    features = build_change_features(
        graph,
        changed_files,
        change_metrics,
    )

    assert len(features) == 1
    assert features[0]["file"] == "src/models.py"
    assert features[0]["direct_impacts"] == 1


def test_unmapped_files_are_skipped():
    """Ignore changed files that are absent from the dependency graph."""

    graph = nx.DiGraph()

    graph.add_node("app.py")

    features = build_change_features(
        graph,
        ["missing.py"],
        {
            "missing.py": {
                "lines_added": 5,
                "lines_deleted": 0,
                "total_changes": 5,
            }
        },
    )

    assert features == []


def test_missing_change_metrics_use_zero():
    """Use zero when a mapped file has no change metrics."""

    graph = nx.DiGraph()

    graph.add_node("app.py")

    features = build_change_features(
        graph,
        ["app.py"],
        {},
    )

    assert len(features) == 1

    record = features[0]

    assert record["lines_added"] == 0
    assert record["lines_deleted"] == 0
    assert record["total_changes"] == 0
    assert record["direct_impacts"] == 0
    assert record["indirect_impacts"] == 0
    assert record["total_impacts"] == 0